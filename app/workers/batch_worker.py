from pathlib import Path

from app.pipelines.extraction_pipeline import ExtractionPipeline


class BatchWorker:

	def __init__(
		self,
		pipeline=None,
		batch_size: int = 10,
		max_retries: int = 0
	):
		if batch_size < 1:
			raise ValueError("batch_size must be at least 1")
		if max_retries < 0:
			raise ValueError("max_retries cannot be negative")

		self.pipeline = pipeline or ExtractionPipeline()
		self.batch_size = batch_size
		self.max_retries = max_retries

	def run(self, file_paths):
		# Materialize iterables so the report can include a total and batches can be sliced.
		file_paths = list(file_paths)
		report = {
			"total": len(file_paths),
			"succeeded": 0,
			"failed": 0,
			"results": [],
			"errors": []
		}

		for start in range(0, len(file_paths), self.batch_size):
			batch = file_paths[start:start + self.batch_size]

			for file_path in batch:
				# Handle failures per file so one bad document does not stop the batch.
				result = self._process_file(file_path)
				if result["status"] == "completed":
					report["succeeded"] += 1
					report["results"].append(result)
				else:
					report["failed"] += 1
					report["errors"].append(result)

		# Summarize the batch without hiding partial success.
		if report["failed"] == 0:
			report["status"] = "completed"
		elif report["succeeded"] == 0:
			report["status"] = "failed"
		else:
			report["status"] = "completed_with_errors"

		return report

	def _process_file(self, file_path):
		# max_retries counts additional attempts after the initial processing attempt.
		for attempt in range(1, self.max_retries + 2):
			try:
				result = self.pipeline.process(str(file_path))
				return {
					**result,
					"status": "completed",
					"attempt": attempt
				}
			except Exception as error:
				if attempt == self.max_retries + 1:
					return {
						"file_name": Path(file_path).name,
						"status": "failed",
						"attempt": attempt,
						"error_type": type(error).__name__,
						"message": str(error)
					}
