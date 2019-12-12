from invoke import Call, Executor

from .context import AutomateContext


class AutomateCall(Call):
    def make_context(self, config):
        return AutomateContext(config)


class AutomateExecutor(Executor):
    def expand_calls(self, calls):
        extended_calls = super().expand_calls(calls)

        ret = []
        for call in extended_calls:
            automate_call = call.clone(into=AutomateCall)
            ret.append(automate_call)

        return ret
