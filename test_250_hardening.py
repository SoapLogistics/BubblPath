import unittest
from solomon_250_hardening import HyperHardeningPipeline

class TestHyperHardening(unittest.TestCase):
    def setUp(self):
        self.pipeline = HyperHardeningPipeline()

    def test_pipeline_initialization(self):
        # Ensure exactly 250 tasks are built
        self.assertEqual(len(self.pipeline.tasks), 250)

    def test_pipeline_execution(self):
        report = self.pipeline.execute_all()

        self.assertEqual(report["total_tasks_run"], 250)
        self.assertEqual(report["successful_tasks"], 250)

        # Verify the sample results contain expected structure
        samples = report["sample_results"]
        self.assertEqual(len(samples), 10)

        # Check first task (Memory sweep)
        self.assertTrue("mem_sweep_1" in samples[0]["task"])

        # Check last task (JIT warm)
        self.assertTrue("jit_warm_250" in samples[-1]["task"])

if __name__ == '__main__':
    unittest.main()
