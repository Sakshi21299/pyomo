#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________
#
# Test NEOS solver interface
#
# Because the Kestrel tests require connections to the NEOS server, and
# that can take quite a while (5-20+ seconds), we will only run these
# tests as part of the nightly suite (i.e., by the CI system as part of
# PR / master tests)
#

import os
import json
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))

import pyutilib.th as unittest

import pyomo.scripting.pyomo_command as main
from pyomo.scripting.util import cleanup
from pyomo.neos.kestrel import kestrelAMPL
import pyomo.neos

import pyomo.environ as pyo

neos_available = False
try:
    if kestrelAMPL().neos is not None:
        neos_available = True
except:
    pass


@unittest.category('nightly')
@unittest.skipIf(not neos_available, "Cannot make connection to NEOS server")
class TestKestrel(unittest.TestCase):

    def test_pyomo_command(self):
        results = os.path.join(currdir, 'result.json')
        args = [
            os.path.join(currdir,'t1.py'),
            '--solver-manager=neos',
            '--solver=cbc',
            '--symbolic-solver-labels',
            '--save-results=%s' % results,
            '-c',
            ]
        try:
            output = main.run(args)
            self.assertEqual(output.errorcode, 0)

            with open(results) as FILE:
                data = json.load(FILE)
            self.assertEqual(
                data['Solver'][0]['Status'], 'ok')
            self.assertAlmostEqual(
                data['Solution'][1]['Status'], 'optimal')
            self.assertAlmostEqual(
                data['Solution'][1]['Objective']['o']['Value'], 1)
            self.assertAlmostEqual(
                data['Solution'][1]['Variable']['x']['Value'], 0.5)
        finally:
            cleanup()
            os.remove(results)

    def test_kestrel_plugin(self):
        m = pyo.ConcreteModel()
        m.x = pyo.Var(bounds=(0,1), initialize=0)
        m.c = pyo.Constraint(expr=m.x <= 0.5)
        m.obj = pyo.Objective(expr=2*m.x, sense=pyo.maximize)

        solver_manager = pyo.SolverManagerFactory('neos')
        results = solver_manager.solve(m, opt='cbc')

        self.assertEqual(results.solver[0].status, pyo.SolverStatus.ok)
        self.assertAlmostEqual(pyo.value(m.x), 0.5)

    def test_doc(self):
        kestrel = kestrelAMPL()
        tmp = [tuple(name.split(':')) for name in kestrel.solvers()]
        solvers = set(v[0].lower() for v in tmp if v[1]=='AMPL')

        doc = pyomo.neos.doc
        dockeys = set(doc.keys())

        self.assertEqual(solvers, dockeys)


@unittest.category('nightly')
@unittest.skipIf(not neos_available, "Cannot make connection to NEOS server")
class TestSolvers_script_min(unittest.TestCase):

    def _model(self):
        m = pyo.ConcreteModel()
        m.x = pyo.Var(bounds=(0,1), initialize=0)
        m.c = pyo.Constraint(expr=m.x <= 0.5)
        m.obj = pyo.Objective(expr=-2*m.x, sense=pyo.minimize)
        return m

    def _run(self, opt):
        m = self._model()
        solver_manager = pyo.SolverManagerFactory('neos')
        results = solver_manager.solve(m, opt=opt)

        self.assertEqual(results.solver[0].status, pyo.SolverStatus.ok)
        self.assertAlmostEqual(pyo.value(m.x), 0.5)

    def test_bonmin(self):
        self._run('bonmin')

    def test_cbc(self):
        self._run('cbc')

    def test_conopt(self):
        self._run('conopt')

    def test_couenne(self):
        self._run('couenne')

    def test_cplex(self):
        self._run('cplex')

    def test_filmint(self):
        self._run('filmint')

    def test_filter(self):
        self._run('filter')

    def test_ipopt(self):
        self._run('ipopt')

    def test_knitro(self):
        self._run('knitro')

    def test_lbfgsb(self):
        self._run('l-bfgs-b')

    def test_lancelot(self):
        self._run('lancelot')

    def test_loqo(self):
        self._run('loqo')

    def test_minlp(self):
        self._run('minlp')

    def test_minos(self):
        self._run('minos')

    def test_minto(self):
        self._run('minto')

    def test_mosek(self):
        self._run('mosek')

    def test_ooqp(self):
        self._run('ooqp')

    def test_path(self):
        self._run('path')

    def test_snopt(self):
        self._run('snopt')

    def test_raposa(self):
        self._run('raposa')

    def test_lgo(self):
        self._run('lgo')


@unittest.category('nightly')
@unittest.skipIf(not neos_available, "Cannot make connection to NEOS server")
class TestSolvers_script_max(TestSolvers_script_min):

    def _model(self):
        m = pyo.ConcreteModel()
        m.x = pyo.Var(bounds=(0,1), initialize=0)
        m.c = pyo.Constraint(expr=m.x <= 0.5)
        m.obj = pyo.Objective(expr=2*m.x, sense=pyo.maximize)
        return m


if __name__ == "__main__":
    unittest.main()
