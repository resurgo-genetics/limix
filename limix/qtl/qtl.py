# Copyright(c) 2014, The LIMIX developers (Christoph Lippert, Paolo Francesco Casale, Oliver Stegle)
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
"""
qtl.py contains wrappers around C++ Limix objects to streamline common tasks in GWAS.
"""

import numpy as np
import scipy.stats as st
import scipy as sp
from limix.stats import qvalues
from limix.qtl.lmm import LMM
import time

def qtl_test_lm(snps,pheno, covs=None, test='lrt',verbose=None):
    """
    Wrapper function for univariate single-variant association testing
    using a linear model. 

    Args:
        snps (ndarray):
            (`N`, `S`) ndarray of `S` SNPs for `N` individuals.
        pheno (ndarray):
            (`N`, `P`) ndarray of `P` phenotype sfor `N` individuals.
            If phenotypes have missing values, then the subset of
            individuals used for each phenotype column will be subsetted.
        covs (ndarray, optional):
            (`N`, `D`) ndarray of `D` covariates for `N` individuals.
            By default, ``covs`` is a (`N`, `1`) array of ones.
        test ({'lrt', 'f'}, optional):
            test statistic.
            'lrt' for likelihood ratio test (default) or 'f' for F-test.
        verbose (bool, optional):
            if True, details such as runtime as displayed.

    Returns:
        :class:`limix.qtl.LMM`: LIMIX LMM object

    Example
    -------

        .. doctest::

            >>> from numpy.random import RandomState
            >>> from limix.qtl import qtl_test_lm
            >>> random = RandomState(1)
            >>>
            >>> N = 100
            >>> S = 1000
            >>>
            >>> snps = (random.rand(N, S) < 0.2).astype(float)
            >>> pheno = random.randn(N, 1)
            >>>
            >>> lm = qtl_test_lm(snps, pheno)
            >>> print(lm.getPv()[:,:4])
            [[ 0.87957928  0.50646269  0.56664012  0.60155451]]
    """
    lm = qtl_test_lmm(snps=snps,pheno=pheno,K=None,covs=covs, test=test,verbose=verbose)
    return lm

def qtl_test_lmm(snps,pheno,K=None,covs=None, test='lrt',NumIntervalsDelta0=100,NumIntervalsDeltaAlt=100,searchDelta=False,verbose=None):
    """
    Wrapper function for univariate single-variant association testing
    using a linear mixed model.

    Args:
        snps (ndarray):
            (`N`, `S`) ndarray of `S` SNPs for `N` individuals.
        pheno (ndarray):
            (`N`, `P`) ndarray of `P` phenotype sfor `N` individuals.
            If phenotypes have missing values, then the subset of
            individuals used for each phenotype column will be subsetted.
        K (ndarray, optional):
            (`N`, `N`) ndarray of LMM-covariance/kinship coefficients (optional)
            If not provided, then standard linear regression is considered.
        covs (ndarray, optional):
            (`N`, `D`) ndarray of `D` covariates for `N` individuals.
            By default, ``covs`` is a (`N`, `1`) array of ones.
        test ({'lrt', 'f'}, optional):
            test statistic.
            'lrt' for likelihood ratio test (default) or 'f' for F-test.
        NumIntervalsDelta0 (int, optional):
            number of steps for delta optimization on the null model.
            By default ``NumIntervalsDelta0`` is 100.
        NumIntervalsDeltaAlt (int, optional):
            number of steps for delta optimization on the alternative model.
            Requires ``searchDelta=True`` to have an effect.
        searchDelta (bool, optional):
            if True, delta optimization on the alternative model is carried out.
            By default ``searchDelta`` is False.
        verbose (bool, optional):
            if True, details such as runtime as displayed.

    Returns:
        :class:`limix.qtl.LMM`: LIMIX LMM object

    Example
    -------

        .. doctest::

            >>> from numpy.random import RandomState
            >>> from numpy import dot
            >>> from limix.qtl import qtl_test_lmm
            >>> random = RandomState(1)
            >>>
            >>> N = 100
            >>> S = 1000
            >>>
            >>> snps = (random.rand(N, S) < 0.2).astype(float)
            >>> pheno = random.randn(N, 1)
            >>> W = random.randn(N, 10)
            >>> kinship = dot(W, W.T) / float(10)
            >>>
            >>> lm = qtl_test_lmm(snps, pheno, kinship)
            >>> print(lm.getPv()[:,:4])
            [[ 0.85712431  0.46681538  0.58717204  0.55894821]]
    """
    lmm_ = LMM(snps=snps, pheno=pheno, K=K, covs=covs, test=test, NumIntervalsDelta0=NumIntervalsDelta0, NumIntervalsDeltaAlt=NumIntervalsDeltaAlt, searchDelta=searchDelta, verbose=verbose)
    return lmm_


def qtl_test_lmm_kronecker(snps,phenos,covs=None,Acovs=None,Asnps=None,K1r=None,K1c=None,K2r=None,K2c=None,trait_covar_type='lowrank_diag',rank=1,NumIntervalsDelta0=100,NumIntervalsDeltaAlt=100,searchDelta=False):
    """
    simple wrapper for kroneckerLMM code

    Args:
        snps:   [N x S] np.array of S SNPs for N individuals (test SNPs)
        phenos: [N x P] np.array of P phenotypes for N individuals
        covs:           list of np.arrays holding covariates. Each covs[i] has one corresponding Acovs[i]
        Acovs:          list of np.arrays holding the phenotype design matrices for covariates.
                        Each covs[i] has one corresponding Acovs[i].
        Asnps:          single np.array of I0 interaction variables to be included in the
                        background model when testing for interaction with Inters
                        If not provided, the alternative model will be the independent model
        K1r:    [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K1c:    [P x P] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K2r:    [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K2c:    [P x P] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        trait_covar_type:     type of covaraince to use. Default 'freeform'. possible values are
                        'freeform': free form optimization,
                        'fixed': use a fixed matrix specified in covar_K0,
                        'diag': optimize a diagonal matrix,
                        'lowrank': optimize a low rank matrix. The rank of the lowrank part is specified in the variable rank,
                        'lowrank_id': optimize a low rank matrix plus the weight of a constant diagonal matrix. The rank of the lowrank part is specified in the variable rank,
                        'lowrank_diag': optimize a low rank matrix plus a free diagonal matrix. The rank of the lowrank part is specified in the variable rank,
                        'block': optimize the weight of a constant P x P block matrix of ones,
                        'block_id': optimize the weight of a constant P x P block matrix of ones plus the weight of a constant diagonal matrix,
                        'block_diag': optimize the weight of a constant P x P block matrix of ones plus a free diagonal matrix,
        rank:           rank of a possible lowrank component (default 1)
        NumIntervalsDelta0:  number of steps for delta optimization on the null model (100)
        NumIntervalsDeltaAlt:number of steps for delta optimization on the alt. model (100), requires searchDelta=True to have an effect.
        searchDelta:    Boolean indicator if delta is optimized during SNP testing (default False)

    Returns:
        CKroneckerLMM object
        P-values for all SNPs from liklelihood ratio test
    """
    try:
        import limix_legacy.deprecated
        import limix_legacy.deprecated as dlimix_legacy
    except ImportError:
        print("Please, install limix-legacy to use this functionality.")
    #0. checks
    N  = phenos.shape[0]
    P  = phenos.shape[1]

    if K1r==None:
        K1r = np.dot(snps,snps.T)
    else:
        assert K1r.shape[0]==N, 'K1r: dimensions dismatch'
        assert K1r.shape[1]==N, 'K1r: dimensions dismatch'

    if K2r==None:
        K2r = np.eye(N)
    else:
        assert K2r.shape[0]==N, 'K2r: dimensions dismatch'
        assert K2r.shape[1]==N, 'K2r: dimensions dismatch'

    covs, Acovs = _updateKronCovs(covs,Acovs,N,P)

    #Asnps can be several designs
    if Asnps is None:
        Asnps = [np.ones([1,P])]
    if (type(Asnps)!=list):
        Asnps = [Asnps]
    assert len(Asnps)>0, "need at least one Snp design matrix"

    #one row per column design matrix
    pv = np.zeros((len(Asnps),snps.shape[1]))

    #1. run GP model to infer suitable covariance structure
    if K1c==None or K2c==None:
        vc = _estimateKronCovariances(phenos=phenos, K1r=K1r, K2r=K2r, K1c=K1c, K2c=K2c, covs=covs, Acovs=Acovs, trait_covar_type=trait_covar_type, rank=rank)
        K1c = vc.getTraitCovar(0)
        K2c = vc.getTraitCovar(1)
    else:
        assert K1c.shape[0]==P, 'K1c: dimensions dismatch'
        assert K1c.shape[1]==P, 'K1c: dimensions dismatch'
        assert K2c.shape[0]==P, 'K2c: dimensions dismatch'
        assert K2c.shape[1]==P, 'K2c: dimensions dismatch'

    #2. run kroneckerLMM

    lmm = limix_legacy.deprecated.CKroneckerLMM()
    lmm.setK1r(K1r)
    lmm.setK1c(K1c)
    lmm.setK2r(K2r)
    lmm.setK2c(K2c)
    lmm.setSNPs(snps)
    #add covariates
    for ic  in range(len(Acovs)):
        lmm.addCovariates(covs[ic],Acovs[ic])
    lmm.setPheno(phenos)


    #delta serch on alt. model?
    if searchDelta:
        lmm.setNumIntervalsAlt(NumIntervalsDeltaAlt)
    else:
        lmm.setNumIntervalsAlt(0)
    lmm.setNumIntervals0(NumIntervalsDelta0)

    for iA in range(len(Asnps)):
        #add SNP design
        lmm.setSNPcoldesign(Asnps[iA])
        lmm.process()
        pv[iA,:] = lmm.getPv()[0]
    return lmm,pv


def qtl_test_interaction_lmm_kronecker(snps,phenos,covs=None,Acovs=None,Asnps1=None,Asnps0=None,K1r=None,K1c=None,K2r=None,K2c=None,trait_covar_type='lowrank_diag',rank=1,NumIntervalsDelta0=100,NumIntervalsDeltaAlt=100,searchDelta=False,return_lmm=False):
    """
    I-variate fixed effects interaction test for phenotype specific SNP effects

    Args:
        snps:   [N x S] np.array of S SNPs for N individuals (test SNPs)
        phenos: [N x P] np.array of P phenotypes for N individuals
        covs:           list of np.arrays holding covariates. Each covs[i] has one corresponding Acovs[i]
        Acovs:          list of np.arrays holding the phenotype design matrices for covariates.
                        Each covs[i] has one corresponding Acovs[i].
        Asnps1:         list of np.arrays of I interaction variables to be tested for N
                        individuals. Note that it is assumed that Asnps0 is already included.
                        If not provided, the alternative model will be the independent model
        Asnps0:         single np.array of I0 interaction variables to be included in the
                        background model when testing for interaction with Inters
        K1r:    [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K1c:    [P x P] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K2r:    [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K2c:    [P x P] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        trait_covar_type:     type of covaraince to use. Default 'freeform'. possible values are
                        'freeform': free form optimization,
                        'fixed': use a fixed matrix specified in covar_K0,
                        'diag': optimize a diagonal matrix,
                        'lowrank': optimize a low rank matrix. The rank of the lowrank part is specified in the variable rank,
                        'lowrank_id': optimize a low rank matrix plus the weight of a constant diagonal matrix. The rank of the lowrank part is specified in the variable rank,
                        'lowrank_diag': optimize a low rank matrix plus a free diagonal matrix. The rank of the lowrank part is specified in the variable rank,
                        'block': optimize the weight of a constant P x P block matrix of ones,
                        'block_id': optimize the weight of a constant P x P block matrix of ones plus the weight of a constant diagonal matrix,
                        'block_diag': optimize the weight of a constant P x P block matrix of ones plus a free diagonal matrix,
        rank:           rank of a possible lowrank component (default 1)
        NumIntervalsDelta0:  number of steps for delta optimization on the null model (100)
        NumIntervalsDeltaAlt:number of steps for delta optimization on the alt. model (100), requires searchDelta=True to have an effect.
        searchDelta:     Carry out delta optimization on the alternative model? if yes We use NumIntervalsDeltaAlt steps
    Returns:
        pv:     P-values of the interaction test
        pv0:    P-values of the null model
        pvAlt:  P-values of the alternative model
    """
    try:
        import limix_legacy.deprecated
        import limix_legacy.deprecated as dlimix_legacy
    except ImportError:
        print("Please, install limix-legacy to use this functionality.")
    S=snps.shape[1]
    #0. checks
    N  = phenos.shape[0]
    P  = phenos.shape[1]

    if K1r==None:
        K1r = np.dot(snps,snps.T)
    else:
        assert K1r.shape[0]==N, 'K1r: dimensions dismatch'
        assert K1r.shape[1]==N, 'K1r: dimensions dismatch'

    if K2r==None:
        K2r = np.eye(N)
    else:
        assert K2r.shape[0]==N, 'K2r: dimensions dismatch'
        assert K2r.shape[1]==N, 'K2r: dimensions dismatch'

    covs,Acovs = _updateKronCovs(covs,Acovs,N,P)

    #Asnps can be several designs
    if (Asnps0 is None):
        Asnps0 = [np.ones([1,P])]
    if Asnps1 is None:
        Asnps1 = [np.eye([P])]
    if (type(Asnps0)!=list):
        Asnps0 = [Asnps0]
    if (type(Asnps1)!=list):
        Asnps1 = [Asnps1]
    assert (len(Asnps0)==1) and (len(Asnps1)>0), "need at least one Snp design matrix for null and alt model"

    #one row per column design matrix
    pv = np.zeros((len(Asnps1),snps.shape[1]))
    lrt = np.zeros((len(Asnps1),snps.shape[1]))
    pvAlt = np.zeros((len(Asnps1),snps.shape[1]))
    lrtAlt = np.zeros((len(Asnps1),snps.shape[1]))

    #1. run GP model to infer suitable covariance structure
    if K1c==None or K2c==None:
        vc = _estimateKronCovariances(phenos=phenos, K1r=K1r, K2r=K2r, K1c=K1c, K2c=K2c, covs=covs, Acovs=Acovs, trait_covar_type=trait_covar_type, rank=rank)
        K1c = vc.getTraitCovar(0)
        K2c = vc.getTraitCovar(1)
    else:
        assert K1c.shape[0]==P, 'K1c: dimensions dismatch'
        assert K1c.shape[1]==P, 'K1c: dimensions dismatch'
        assert K2c.shape[0]==P, 'K2c: dimensions dismatch'
        assert K2c.shape[1]==P, 'K2c: dimensions dismatch'

    #2. run kroneckerLMM for null model
    lmm = limix_legacy.deprecated.CKroneckerLMM()
    lmm.setK1r(K1r)
    lmm.setK1c(K1c)
    lmm.setK2r(K2r)
    lmm.setK2c(K2c)
    lmm.setSNPs(snps)
    #add covariates
    for ic  in range(len(Acovs)):
        lmm.addCovariates(covs[ic],Acovs[ic])
    lmm.setPheno(phenos)

    #delta serch on alt. model?
    if searchDelta:
        lmm.setNumIntervalsAlt(NumIntervalsDeltaAlt)
        lmm.setNumIntervals0_inter(NumIntervalsDeltaAlt)
    else:
        lmm.setNumIntervalsAlt(0)
        lmm.setNumIntervals0_inter(0)


    lmm.setNumIntervals0(NumIntervalsDelta0)
    #add SNP design
    lmm.setSNPcoldesign0_inter(Asnps0[0])
    for iA in range(len(Asnps1)):
        lmm.setSNPcoldesign(Asnps1[iA])
        lmm.process()

        pvAlt[iA,:] = lmm.getPv()[0]
        pv[iA,:] = lmm.getPv()[1]
        pv0 = lmm.getPv()[2][np.newaxis,:]
    if return_lmm:
        return pv,pv0,pvAlt,lmm
    else:
        return pv,pv0,pvAlt


def qtl_test_interaction_lmm(snps,pheno,Inter,Inter0=None,covs=None,K=None,test='lrt'):
    """
    I-variate fixed effects interaction test for phenotype specific SNP effects

    Args:
        snps:   [N x S] np.array of S SNPs for N individuals (test SNPs)
        pheno:  [N x 1] np.array of 1 phenotype for N individuals
        Inter:  [N x I] np.array of I interaction variables to be tested for N
                        individuals (optional). If not provided, only the SNP is
                        included in the null model.
        Inter0: [N x I0] np.array of I0 interaction variables to be included in the
                         background model when testing for interaction with Inter
        covs:   [N x D] np.array of D covariates for N individuals
        K:      [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        test:    'lrt' for likelihood ratio test (default) or 'f' for F-test

    Returns:
        limix LMM object
    """
    try:
        import limix_legacy.deprecated
        import limix_legacy.deprecated as dlimix_legacy
    except ImportError:
        print("Please, install limix-legacy to use this functionality.")
    N=snps.shape[0]
    if covs is None:
        covs = np.ones((N,1))
    if K is None:
        K = np.eye(N)
    if Inter0 is None:
        Inter0=np.ones([N,1])
    assert (pheno.shape[0]==N and K.shape[0]==N and K.shape[1]==N and covs.shape[0]==N and Inter0.shape[0]==N and Inter.shape[0]==N), "shapes missmatch"
    lmi = limix_legacy.deprecated.CInteractLMM()
    lmi.setK(K)
    lmi.setSNPs(snps)
    lmi.setPheno(pheno)
    lmi.setCovs(covs)
    lmi.setInter0(Inter0)
    lmi.setInter(Inter)
    if test=='lrt':
        lmi.setTestStatistics(lmi.TEST_LRT)
    elif test=='f':
        lmi.setTestStatistics(lmi.TEST_F)
    else:
        print(test)
        raise NotImplementedError("only f or lrt are implemented")
    lmi.process()
    return lmi


""" MULTI LOCUS MODEL """


def forward_lmm(snps,pheno,K=None,covs=None,qvalues=False,threshold=5e-8,maxiter=2,test='lrt',verbose=None,**kw_args):
    """
    univariate fixed effects test with forward selection

    Args:
        snps:   [N x S] np.array of S SNPs for N individuals (test SNPs)
        pheno:  [N x 1] np.array of 1 phenotype for N individuals
        K:      [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        covs:   [N x D] np.array of D covariates for N individuals
        threshold:      (float) P-value thrashold for inclusion in forward selection (default 5e-8)
        maxiter:        (int) maximum number of interaction scans. First scan is
                        without inclusion, so maxiter-1 inclusions can be performed. (default 2)
        test:           'lrt' for likelihood ratio test (default) or 'f' for F-test
        verbose: print verbose output? (False)

    Returns:
        lm:     limix LMM object
        RV:     dictionary
                RV['iadded']:   array of indices of SNPs included in order of inclusion
                RV['pvadded']:  array of Pvalues obtained by the included SNPs in iteration
                                before inclusion
                RV['pvall']:    [Nadded x S] np.array of Pvalues for all iterations
    """
    try:
        import limix_legacy.deprecated
        import limix_legacy.deprecated as dlimix_legacy
    except ImportError:
        print("Please, install limix-legacy to use this functionality.")
    verbose = dlimix_legacy.getVerbose(verbose)

    if K is None:
        K=np.eye(snps.shape[0])
    if covs is None:
        covs = np.ones((snps.shape[0],1))
    #assert single trait
    assert pheno.shape[1]==1, 'forward_lmm only supports single phenotypes'

    lm = qtl_test_lmm(snps,pheno,K=K,covs=covs,test=test,**kw_args)
    pvall = []
    pv = lm.getPv().ravel()
    #hack to avoid issues with degenerate pv
    pv[sp.isnan(pv)] = 1
    pvall.append(pv)
    imin= pv.argmin()
    niter = 1
    #start stuff
    iadded = []
    pvadded = []
    qvadded = []
    if qvalues:
        assert pv.shape[0]==1, "This is untested with the fdr package. pv.shape[0]==1 failed"
        qvall = []
        qv  = qvalues(pv)
        qvall.append(qv)
        score=qv.min()
    else:
        score=pv.min()
    while (score<threshold) and niter<maxiter:
        t0=time.time()
        iadded.append(imin)
        pvadded.append(pv[imin])
        if qvalues:
            qvadded.append(qv[0,imin])
        covs=np.concatenate((covs,snps[:,imin:(imin+1)]),1)
        lm.setCovs(covs)
        lm.process()
        pv = lm.getPv().ravel()
        pv[sp.isnan(pv)] = 1
        pvall.append(pv)
        imin= pv.argmin()
        if qvalues:
            qv = qvalues(pv)
            qvall[niter:niter+1,:] = qv
            score = qv.min()
        else:
            score = pv.min()
        t1=time.time()
        if verbose:
            print(("finished GWAS testing in %.2f seconds" %(t1-t0)))
        niter=niter+1
    RV = {}
    RV['iadded']  = iadded
    RV['pvadded'] = pvadded
    RV['pvall']   = np.array(pvall)
    if qvalues:
        RV['qvall'] = np.array(qvall)
        RV['qvadded'] = qvadded
    return lm,RV


#TOOD: use **kw_args to forward params.. see below
def forward_lmm_kronecker(snps,phenos,Asnps=None,Acond=None,K1r=None,K1c=None,K2r=None,K2c=None,covs=None,Acovs=None,threshold=5e-8,maxiter=2,qvalues=False, update_covariances = False,verbose=None,**kw_args):
    """
    Kronecker fixed effects test with forward selection

    Args:
        snps:   [N x S] np.array of S SNPs for N individuals (test SNPs)
        pheno:  [N x P] np.array of 1 phenotype for N individuals
        K:      [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        covs:   [N x D] np.array of D covariates for N individuals
        threshold:      (float) P-value thrashold for inclusion in forward selection (default 5e-8)
        maxiter:        (int) maximum number of interaction scans. First scan is
                        without inclusion, so maxiter-1 inclusions can be performed. (default 2)
        qvalues:        Use q-value threshold and return q-values in addition (default False)
        update_covar:   Boolean indicator if covariances should be re-estimated after each forward step (default False)

    Returns:
        lm:             lmix LMMi object
        resultStruct with elements:
            iadded:         array of indices of SNPs included in order of inclusion
            pvadded:        array of Pvalues obtained by the included SNPs in iteration
                            before inclusion
            pvall:     [Nadded x S] np.array of Pvalues for all iterations.
        Optional:      corresponding q-values
            qvadded
            qvall
    """
    try:
        import limix_legacy.deprecated
        import limix_legacy.deprecated as dlimix_legacy
    except ImportError:
        print("Please, install limix-legacy to use this functionality.")
    verbose = dlimix_legacy.getVerbose(verbose)
    #0. checks
    N  = phenos.shape[0]
    P  = phenos.shape[1]

    if K1r==None:
        K1r = np.dot(snps,snps.T)
    else:
        assert K1r.shape[0]==N, 'K1r: dimensions dismatch'
        assert K1r.shape[1]==N, 'K1r: dimensions dismatch'

    if K2r==None:
        K2r = np.eye(N)
    else:
        assert K2r.shape[0]==N, 'K2r: dimensions dismatch'
        assert K2r.shape[1]==N, 'K2r: dimensions dismatch'

    covs,Acovs = _updateKronCovs(covs,Acovs,N,P)

    if Asnps is None:
        Asnps = [np.ones([1,P])]
    if (type(Asnps)!=list):
        Asnps = [Asnps]
    assert len(Asnps)>0, "need at least one Snp design matrix"

    if Acond is None:
        Acond = Asnps
    if (type(Acond)!=list):
        Acond = [Acond]
    assert len(Acond)>0, "need at least one Snp design matrix"

    #1. run GP model to infer suitable covariance structure
    if K1c==None or K2c==None:
        vc = _estimateKronCovariances(phenos=phenos, K1r=K1r, K2r=K2r, K1c=K1c, K2c=K2c, covs=covs, Acovs=Acovs, **kw_args)
        K1c = vc.getTraitCovar(0)
        K2c = vc.getTraitCovar(1)
    else:
        vc = None
        assert K1c.shape[0]==P, 'K1c: dimensions dismatch'
        assert K1c.shape[1]==P, 'K1c: dimensions dismatch'
        assert K2c.shape[0]==P, 'K2c: dimensions dismatch'
        assert K2c.shape[1]==P, 'K2c: dimensions dismatch'
    t0 = time.time()
    lm,pv = qtl_test_lmm_kronecker(snps=snps,phenos=phenos,Asnps=Asnps,K1r=K1r,K2r=K2r,K1c=K1c,K2c=K2c,covs=covs,Acovs=Acovs)

    #get pv
    #start stuff
    iadded = []
    pvadded = []
    qvadded = []
    time_el = []
    pvall = []
    qvall = None
    t1=time.time()
    if verbose:
        print(("finished GWAS testing in %.2f seconds" %(t1-t0)))
    time_el.append(t1-t0)
    pvall.append(pv)
    imin= np.unravel_index(pv.argmin(),pv.shape)
    score=pv[imin].min()
    niter = 1
    if qvalues:
        assert pv.shape[0]==1, "This is untested with the fdr package. pv.shape[0]==1 failed"
        qvall = []
        qv  = qvalues(pv)
        qvall.append(qv)
        score=qv[imin]
    #loop:
    while (score<threshold) and niter<maxiter:
        t0=time.time()
        pvadded.append(pv[imin])
        iadded.append(imin)
        if qvalues:
            qvadded.append(qv[imin])
        if update_covariances and vc is not None:
            vc.addFixedTerm(snps[:,imin[1]:(imin[1]+1)],Acond[imin[0]])
            vc.setScales()#CL: don't know what this does, but findLocalOptima crashes becahuse vc.noisPos=None
            vc.findLocalOptima(fast=True)
            K1c = vc.getTraitCovar(0)
            K2c = vc.getTraitCovar(1)
            lm.setK1c(K1c)
            lm.setK2c(K2c)
        lm.addCovariates(snps[:,imin[1]:(imin[1]+1)],Acond[imin[0]])
        for i in range(len(Asnps)):
            #add SNP design
            lm.setSNPcoldesign(Asnps[i])
            lm.process()
            pv[i,:] = lm.getPv()[0]
        pvall.append(pv.ravel())
        imin= np.unravel_index(pv.argmin(),pv.shape)
        if qvalues:
            qv = qvalues(pv)
            qvall[niter:niter+1,:] = qv
            score = qv[imin].min()
        else:
            score = pv[imin].min()
        t1=time.time()
        if verbose:
            print(("finished GWAS testing in %.2f seconds" %(t1-t0)))
        time_el.append(t1-t0)
        niter=niter+1
    RV = {}
    RV['iadded']  = iadded
    RV['pvadded'] = pvadded
    RV['pvall']   = np.array(pvall)
    RV['time_el'] = time_el
    if qvalues:
        RV['qvall'] = qvall
        RV['qvadded'] = qvadded
    return lm,RV



""" INTERNAL """
def _estimateKronCovariances(phenos,K1r=None,K1c=None,K2r=None,K2c=None,covs=None,Acovs=None,trait_covar_type='lowrank_diag',rank=1,lambd=None,verbose=True,init_method='random',old_opt=True):
    """
    estimates the background covariance model before testing

    Args:
        phenos: [N x P] np.array of P phenotypes for N individuals
        K1r:    [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K1c:    [P x P] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K2r:    [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        K2c:    [P x P] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        covs:           list of np.arrays holding covariates. Each covs[i] has one corresponding Acovs[i]
        Acovs:          list of np.arrays holding the phenotype design matrices for covariates.
                        Each covs[i] has one corresponding Acovs[i].
        trait_covar_type:     type of covaraince to use. Default 'freeform'. possible values are
                        'freeform': free form optimization,
                        'fixed': use a fixed matrix specified in covar_K0,
                        'diag': optimize a diagonal matrix,
                        'lowrank': optimize a low rank matrix. The rank of the lowrank part is specified in the variable rank,
                        'lowrank_id': optimize a low rank matrix plus the weight of a constant diagonal matrix. The rank of the lowrank part is specified in the variable rank,
                        'lowrank_diag': optimize a low rank matrix plus a free diagonal matrix. The rank of the lowrank part is specified in the variable rank,
                        'block': optimize the weight of a constant P x P block matrix of ones,
                        'block_id': optimize the weight of a constant P x P block matrix of ones plus the weight of a constant diagonal matrix,
                        'block_diag': optimize the weight of a constant P x P block matrix of ones plus a free diagonal matrix,
        rank:           rank of a possible lowrank component (default 1)

    Returns:
        VarianceDecomposition object
    """
    try:
        import limix_legacy.deprecated
        import limix_legacy.deprecated as dlimix_legacy
        import limix_legacy.deprecated.VarianceDecomposition as VAR
    except ImportError:
        print("Please, install limix-legacy to use this functionality.")

    # from . import varianceDecomposition as VAR
    print(".. Training the backgrond covariance with a GP model")
    vc = VAR.VarianceDecomposition(phenos)
    if K1r is not None:
        vc.addRandomEffect(K1r,trait_covar_type=trait_covar_type,rank=rank)
    if K2r is not None:
        #TODO: fix this; forces second term to be the noise covariance
        vc.addRandomEffect(is_noise=True,K=K2r,trait_covar_type=trait_covar_type,rank=rank)
    for ic  in range(len(Acovs)):
        vc.addFixedEffect(covs[ic],Acovs[ic])
    start = time.time()
    if old_opt:
        conv = vc.optimize(fast=True)
    elif lambd is not None:
        conv = vc.optimize(init_method=init_method,verbose=verbose,lambd=lambd)
    else:
        conv = vc.optimize(init_method=init_method,verbose=verbose)
    assert conv, "Variance Decomposition has not converged"
    time_el = time.time()-start
    print(("Background model trained in %.2f s" % time_el))
    return vc

def _updateKronCovs(covs,Acovs,N,P):
    """
    make sure that covs and Acovs are lists
    """
    if (covs is None) and (Acovs is None):
        covs = [np.ones([N,1])]
        Acovs = [np.eye(P)]

    if Acovs is None or covs is None:
        raise Exception("Either Acovs or covs is None, while the other isn't")

    if (type(Acovs)!=list) and (type(covs)!=list):
        Acovs= [Acovs]
        covs = [covs]
    if (type(covs)!=list) or (type(Acovs)!=list) or (len(covs)!=len(Acovs)):
        raise Exception("Either Acovs or covs is not a list or they missmatch in length")
    return covs, Acovs


#TODO: we need to fix. THis does not work as interact_GxE is not existing
#I vote we also use **kw_args to forward parameters to interact_Gxe?
def qtl_test_interaction_GxG(pheno,snps1,snps2=None,K=None,covs=None,test='lrt'):
    """
    Epistasis test between two sets of SNPs

    Args:
        pheno:  [N x 1] np.array of 1 phenotype for N individuals
        snps1:  [N x S1] np.array of S1 SNPs for N individuals
        snps2:  [N x S2] np.array of S2 SNPs for N individuals
        K:      [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        covs:   [N x D] np.array of D covariates for N individuals
        test:    'lrt' for likelihood ratio test (default) or 'f' for F-test

    Returns:
        pv:     [S2 x S1] np.array of P values for epistasis tests beten all SNPs in
                snps1 and snps2
    """
    if K is None:
        K=np.eye(N)
    N=snps1.shape[0]
    if snps2 is None:
        snps2 = snps1
    return qtl_test_interaction_GxE_1dof(snps=snps1,pheno=pheno,env=snps2,covs=covs,K=K,test=test)


def qtl_test_interaction_GxE_1dof(snps,pheno,env,K=None,covs=None, test='lrt',verbose=None):
    """
    Univariate GxE fixed effects interaction linear mixed model test for all
    pairs of SNPs and environmental variables.

    Args:
        snps:   [N x S] np.array of S SNPs for N individuals
        pheno:  [N x 1] np.array of 1 phenotype for N individuals
        env:    [N x E] np.array of E environmental variables for N individuals
        K:      [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        covs:   [N x D] np.array of D covariates for N individuals
        test:    'lrt' for likelihood ratio test (default) or 'f' for F-test
        verbose: print verbose output? (False)

    Returns:
        pv:     [E x S] np.array of P values for interaction tests between all
                E environmental variables and all S SNPs
    """
    try:
        import limix_legacy.deprecated as dlimix_legacy
    except ImportError:
        print("Please, install limix-legacy to use this functionality.")
    verbose = dlimix_legacy.getVerbose(verbose)
    N=snps.shape[0]
    if K is None:
        K=np.eye(N)
    if covs is None:
        covs = np.ones((N,1))
    assert (env.shape[0]==N and pheno.shape[0]==N and K.shape[0]==N and K.shape[1]==N and covs.shape[0]==N), "shapes missmatch"
    Inter0 = np.ones((N,1))
    pv = np.zeros((env.shape[1],snps.shape[1]))
    if verbose:
        print(("starting %i interaction scans for %i SNPs each." % (env.shape[1], snps.shape[1])))
    t0=time.time()
    for i in range(env.shape[1]):
        t0_i = time.time()
        cov_i = np.concatenate((covs,env[:,i:(i+1)]),1)
        lm_i = qtl_test_interaction_lmm(snps=snps,pheno=pheno,covs=cov_i,Inter=env[:,i:(i+1)],Inter0=Inter0,test=test)
        pv[i,:]=lm_i.getPv()[0,:]
        t1_i = time.time()
        if verbose:
            print(("Finished %i out of %i interaction scans in %.2f seconds."%((i+1),env.shape[1],(t1_i-t0_i))))
    t1 = time.time()
    print(("-----------------------------------------------------------\nFinished all %i interaction scans in %.2f seconds."%(env.shape[1],(t1-t0))))
    return pv


def phenSpecificEffects(snps,pheno1,pheno2,K=None,covs=None,test='lrt'):
    """
    Univariate fixed effects interaction test for phenotype specific SNP effects

    Args:
        snps:   [N x S] np.array of S SNPs for N individuals (test SNPs)
        pheno1: [N x 1] np.array of 1 phenotype for N individuals
        pheno2: [N x 1] np.array of 1 phenotype for N individuals
        K:      [N x N] np.array of LMM-covariance/kinship koefficients (optional)
                        If not provided, then linear regression analysis is performed
        covs:   [N x D] np.array of D covariates for N individuals
        test:    'lrt' for likelihood ratio test (default) or 'f' for F-test

    Returns:
        limix LMM object
    """
    N=snps.shape[0]
    if K is None:
        K=np.eye(N)
    assert (pheno1.shape[1]==pheno2.shape[1]), "Only consider equal number of phenotype dimensions"
    if covs is None:
        covs = np.ones(N,1)
    assert (pheno1.shape[1]==1 and pheno2.shape[1]==1 and pheno1.shape[0]==N and pheno2.shape[0]==N and K.shape[0]==N and K.shape[1]==N and covs.shape[0]==N), "shapes missmatch"
    Inter = np.zeros((N*2,1))
    Inter[0:N,0]=1
    Inter0 = np.ones((N*2,1))
    Yinter=np.concatenate((pheno1,pheno2),0)
    Xinter = np.tile(snps,(2,1))
    Covitner= np.tile(covs(2,1))
    lm = qtl_test_interaction_lmm(snps=Xinter,pheno=Yinter,covs=Covinter,Inter=Inter,Inter0=Inter0,test=test)
    return lm
