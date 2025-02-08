from langchain.callbacks.base import BaseCallbackHandler
from loguru import logger

class CustomEventHandler(BaseCallbackHandler):
    """A custom callback handler to log chain events and tool usage."""

    def on_chain_start(self, serialized, inputs, **kwargs):
        logger.info("Chain started with inputs: {}", inputs)

    def on_chain_end(self, outputs, **kwargs):
        logger.info("Chain ended with outputs: {}", outputs)

    def on_chain_error(self, error, **kwargs):
        logger.error("Chain error: {}", error)

    def on_tool_start(self, serialized, input_text, **kwargs):
        logger.info("Tool started with input: {}", input_text)

    def on_tool_end(self, output, **kwargs):
        logger.info("Tool finished with output: {}", output)

    def on_tool_error(self, error, **kwargs):
        logger.error("Tool error: {}", error)
