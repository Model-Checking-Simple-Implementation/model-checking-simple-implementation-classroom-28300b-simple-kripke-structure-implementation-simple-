class Proposition:
    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def propositions(*args) -> list["Proposition"]:
        assert len(args) > 0 and all(isinstance(arg, str) for arg in args), "Only non-empty list of strings is allowed. "
        return [Proposition(name) for name in args]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class State:
    def __init__(self, name: str, labels: set[Proposition]) -> None:
        pass

    def make_transition(self, state: "State") -> None:
        pass


class KripkeStructure:
    def __init__(self, initial_states: set[State], propositions: set[Proposition]) -> None:
        pass

    def is_valid(self) -> bool:
        pass