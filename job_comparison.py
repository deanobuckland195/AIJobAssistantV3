def find_best_job(job_comparisons):
    if not job_comparisons:
        return None

    return max(job_comparisons, key=lambda job: job["score"])