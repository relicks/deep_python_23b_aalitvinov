from unittest import IsolatedAsyncioTestCase


class AsyncArguments(IsolatedAsyncioTestCase):
    async def test_something_async(self):
        async def addition(x, y):
            return x + y

        assert await addition(2, 2) == 4
