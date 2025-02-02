import os, sys, unittest
import numpy as np
import scipy.sparse as sparse

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from ddlite import *

class TestInference(unittest.TestCase):
    
    def setUp(self):
        self.ridge = 0
        self.lasso = 1
    
    def tearDown(self):
        pass
    
    def logistic_regression_small(self, alpha, mu):
        X, w0, gt = self._problem(n=250, nlf=50, lf_prior=0.4, lf_mean=0.7,
                                  lf_sd=0.25, nf=250, f_prior=0.2, f_mean=0.6,
                                  f_sd=0.25)
        w = learn_elasticnet_logreg(X, maxIter=500, tol=1e-4, w0=w0,
                                    sample=False, alpha=alpha, mu_seq=mu, 
                                    rate=0.01, verbose=True)[mu]
        self.assertGreater(np.mean(np.sign(X.dot(w)) == gt), 0.85)
    
    def test_ridge_logistic_regression_small_1(self):
        print "Running small ridge logistic regression test 1"
        self.logistic_regression_small(self.ridge, 1e-6)
        
    def test_lasso_logistic_regression_small_1(self):
        print "Running small lasso logistic regression test 1"
        self.logistic_regression_small(self.lasso, 1e-6)
        
    def test_ridge_logistic_regression_small_2(self):
        print "Running small ridge logistic regression test 2"
        self.logistic_regression_small(self.ridge, 1e-4)
        
    def test_lasso_logistic_regression_small_2(self):
        print "Running small lasso logistic regression test 2"
        self.logistic_regression_small(self.lasso, 1e-4)

    def logistic_regression_large(self, alpha, mu):
        X, w0, gt = self._problem(n=1000, nlf=100, lf_prior=0.2, lf_mean=0.7,
                                  lf_sd=0.25, nf=5000, f_prior=0.05, f_mean=0.6,
                                  f_sd=0.25)
        w = learn_elasticnet_logreg(X, maxIter=1000, tol=1e-4, w0=w0,
                                    sample=False, alpha=alpha, mu_seq=mu, 
                                    rate=0.01, verbose=True)[mu]
        self.assertGreater(np.mean(np.sign(X.dot(w)) == gt), 0.85)
        
    def test_ridge_logistic_regression_large_1(self):
        print "Running large ridge logistic regression test 1"
        self.logistic_regression_large(self.ridge, 1e-6)
        
    def test_lasso_logistic_regression_large_1(self):
        print "Running large lasso logistic regression test 1"
        self.logistic_regression_large(self.lasso, 1e-6)
        
    def test_ridge_logistic_regression_large_2(self):
        print "Running large ridge logistic regression test 2"
        self.logistic_regression_large(self.ridge, 1e-4)
        
    def test_lasso_logistic_regression_large_2(self):
        print "Running large lasso logistic regression test 2"
        self.logistic_regression_large(self.lasso, 1e-4)
        
    def test_logistic_regression_sparse(self):
        print "Running logistic regression test with sparse operations"
        X, w0, gt = self._problem(n=500, nlf=75, lf_prior=0.3, lf_mean=0.7,
                                  lf_sd=0.25, nf=1000, f_prior=0.1, f_mean=0.6,
                                  f_sd=0.25)
        mu = 1e-4
        w_s = learn_elasticnet_logreg(X, maxIter=2500, tol=1e-4, w0=w0,
                                      sample=False, alpha=self.ridge,
                                      mu_seq=mu, rate=0.01, verbose=True)[mu]
        w_d = learn_elasticnet_logreg(np.asarray(X.todense()), maxIter=2500,
                                      tol=1e-4, w0=w0, sample=False,
                                      alpha=self.ridge, mu_seq=mu, rate=0.01,
                                      verbose=True)[mu]
        # Check sparse solution is close to dense solution
        self.assertLessEqual(np.linalg.norm(w_s - w_d), 1e-6)
        
    def test_logistic_regression_sample(self):
        print "Running logistic regression test with sparse operations"
        X, w0, gt = self._problem(n=500, nlf=75, lf_prior=0.3, lf_mean=0.7,
                                  lf_sd=0.25, nf=1000, f_prior=0.1, f_mean=0.6,
                                  f_sd=0.25)
        mu = 1e-4
        w_d = learn_elasticnet_logreg(X, maxIter=2500, tol=1e-4, w0=w0,
                                      sample=False, alpha=self.ridge,
                                      mu_seq=mu, rate=0.01, verbose=True)[mu]
        w_s = learn_elasticnet_logreg(X, maxIter=2500, tol=1e-4, w0=w0,
                                      sample=True, n_samples=200,
                                      alpha=self.ridge, mu_seq=mu, rate=0.01,
                                      verbose=True)[mu]
        # Check sample marginals are close to deterministic solutio
        ld, ls = odds_to_prob(X.dot(w_d)), odds_to_prob(X.dot(w_s))
        self.assertLessEqual(np.linalg.norm(ld-ls) / np.linalg.norm(ld), 0.05)
                             
    def test_logistic_regression_cv(self):
        print "Running logistic regression test with cross validation"
        X, w0, gt = self._problem(n=500, nlf=50, lf_prior=0.2, lf_mean=0.6,
                                  lf_sd=0.25, nf=800, f_prior=0.1, f_mean=0.55,
                                  f_sd=0.25)
        mu_seq = [1e6, 1, 1e-12]
        w = cv_elasticnet_logreg(X, nfolds=3, w0=w0, mu_seq=mu_seq, plot=False,
                                 alpha=self.ridge, opt_1se=True, verbose=True,
                                 maxIter=2500, tol=1e-4, sample=False,
                                 rate=0.01)
        w_all = [learn_elasticnet_logreg(X, maxIter=2500, tol=1e-4, w0=w0,
                                         sample=False, alpha=self.ridge,
                                         mu_seq=mu, rate=0.01, verbose=True)[mu]
                for mu in mu_seq]
        for wp in w_all:
            self.assertGreaterEqual(np.mean(np.sign(X.dot(w)) == gt),
                                    np.mean(np.sign(X.dot(wp)) == gt)-0.05)
                         
                         
    def _problem(self, n, nlf, lf_prior, lf_mean, lf_sd, nf, f_prior, f_mean, f_sd):
        # Gen gt  
        gt = np.concatenate([np.ones((np.floor(n/2))), 
                             -1 * np.ones((n-np.floor(n/2)))])
        ##### LF #####
        # LF label?
        lf_label = np.random.rand(n, nlf) < lf_prior
        # LF correct?
        lf_corr = ((lf_sd * np.random.randn(n, nlf) + lf_mean) > 0.5).astype(float)
        lf_corr[lf_corr == 0] = -1
        # LF
        LF = (lf_corr * gt[:, np.newaxis]) * lf_label
        ##### F #####
        # F label?
        f_label = np.random.rand(n, nf) < f_prior
        # F correct?
        f_corr = ((f_sd * np.random.randn(n, nf) + f_mean) > 0.5).astype(float)
        f_corr[f_corr == 0] = -1
        # LF
        F = (f_corr * gt[:, np.newaxis]) * f_label
        ##### X #####
        LF = sparse.csr_matrix(LF)
        F = sparse.csr_matrix(F)
        # Join matrices
        X_sparse = sparse.hstack([LF, F], format='csr')
        # Set initial weights
        w0 = np.concatenate([np.ones(nlf), np.zeros(nf)])
        return X_sparse, w0, gt


if __name__ == '__main__':
    unittest.main()
    