from DockingStats import *
import random
import optparse
import pylab
import numpy
import os
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from numpy import linalg


def main(refname): 
    keys=['h36', 'conn', 'npxxy', 'bulge']
    ligands=['bi', 'car', 'apo']
    refpops=numpy.loadtxt('bi/cent-structural-data/Populations.dat')
    refstates=numpy.loadtxt('./bi/bi_cent_agonist_auc_ci.txt', usecols=(0,),
            dtype=int)
    cutoff=min(refpops[refstates])
    if len(ligands) < 3:
        print "using only ligand data"
    aucnames=['agonist', 'antagonist', 'types']
    allsystems=dict()
    allrandom=dict()
    for aucname in aucnames:
        allsystems[aucname]=[]
        for sys in ligands:
            allrandom[sys]=numpy.loadtxt('./%s/%s_rando_%s_auc_ci.txt' % (sys, sys, aucname), usecols=(1,))
            states=numpy.loadtxt('./%s/%s_%s_%s_auc_ci.txt' % (sys, sys, refname, aucname), usecols=(0,), dtype=int)
            dir='./%s/cent-structural-data/' % sys
            pops=numpy.loadtxt('%s/Populations.dat' % dir)
            aucs=numpy.loadtxt('./%s/%s_%s_%s_auc_ci.txt' % (sys, sys, refname, aucname), usecols=(1,))
            pops=pops[states]
            frames=numpy.where(pops>= cutoff)[0]
            pops=pops[frames]
            states=states[frames]
            numpy.savetxt('%s/filter_states.txt' % sys, states)
            aucs=aucs[frames]
            # make system class for AUC
            SD=SystemDock(sys, states, aucs, pops)
            pathfile=open('%s/%s_paths.txt' % (sys, sys))
            max_score, op_scores=get_ref_scores(keys)
            if sys=='bi':
                print "max score is ", max_score
            SD.get_path_scores(dir, pathfile, keys, op_scores)
            slope, intercept, R, pval, std_err = stats.linregress(SD.pathscores, SD.aucs)
            print sys, "R2 Test Path Progress %s AUC: " % get_label(aucname),  round(R,2) , pval
            #scatter_fits(SD.pathscores, SD.aucs, R, pval, aucname, show=True)
            allsystems[aucname].append(SD)
        chi2, pval=chi2_test([x.aucs for x in allsystems[aucname]])
        print "Chi2 Test for Ligand State %s AUC" % get_label(aucname), chi2, pval
        if reduce==True:
            ohandle=open('%s_reduced_allvalues.dat' % aucname, 'w')
        else:
            ohandle=open('%s_allvalues.dat' % aucname, 'w')
        allprogress=dict()
        for system in allsystems[aucname]: 
            if reduce==True:
                modify_scores(length)
                target=system.reducepathscores
                print "Reduced Path Scores"
            else:
                target=system.pathscores
            for (score, val) in zip(target, system.aucs):
                if score>=9:
                    score=9.0
                if score not in allprogress.keys():
                    allprogress[score]=[]
                allprogress[score].append(val)
        chi2, pval=chi2_test([allprogress[x] for x in sorted(allprogress.keys())])
        print "Chi2 Test for Path Progress %s AUC" % get_label(aucname), chi2, pval
        randomsample=[]
        for values in allrandom.values():
            for i in values:
                randomsample.append(i)
        randomsample=numpy.array(randomsample)
        for key in sorted(allprogress.keys()):
            ohandle.write('%s\t%s\n' % (key, allprogress[key])) 
            indices=bootstrap(len(randomsample), len(allprogress[key]))
            print "random mean= ", numpy.mean(randomsample[indices]),  "Path %s mean= " % key, numpy.mean(allprogress[key])
            print "random variance= ", numpy.var(randomsample[indices]),  "Path %s variance= " % key, numpy.var(allprogress[key])
            t, pval=ttest_ind(allprogress[key], randomsample[indices],
            axis=0, equal_var=False)
            print "Path %s population difference t= " % key, t, "pval= ", pval


def parse_commandline():
    parser = optparse.OptionParser()
    parser.add_option('-r', '--refname', dest='refname',
                      help='refname AUC set')
    #parser.add_option('-x', '--testname', dest='testname',
    #                  help='test AUC set')
    (options, args) = parser.parse_args()
    return (options, args)

if __name__ == "__main__":
    (options, args) = parse_commandline()
    main(refname=options.refname)


