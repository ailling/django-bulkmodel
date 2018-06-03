import asyncio
import collections


class ConcurrentExecutor(object):
    """
    Executes functions concurrently that would normally block and makes the results available
    as a memory of the object instance

    """
    def __init__(self, jobs):
        self.jobs = jobs

        # results from running the blocking jobs
        self.results = []


    async def _asynchronous(self):
        # get a reference to the running loop
        loop = asyncio.get_event_loop()

        futures = []
        for job in self.jobs:
            if isinstance(job, collections.Iterable):
                f = job[0]
                args = job[1:]
                futures.append(
                    loop.run_in_executor(None, f, *args)
                )

            elif callable(job):
                futures.append(
                    loop.run_in_executor(None, job)
                )

        for i, future in enumerate(asyncio.as_completed(futures)):
            result = await future
            self.results.append(result)


    def run_async(self):
        """
        Run jobs asynchronously

        :return:
        """
        ioloop = asyncio.new_event_loop()
        ioloop.run_until_complete(self._asynchronous())
        ioloop.close()

        return self.results
