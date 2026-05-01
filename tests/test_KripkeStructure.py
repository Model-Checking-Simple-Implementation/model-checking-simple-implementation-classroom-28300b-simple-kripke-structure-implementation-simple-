import pytest

from KripkeStructure import Proposition, State, KripkeStructure


def test_proposition_factory():
    props = Proposition.propositions("p", "q")
    assert len(props) == 2
    assert str(props[0]) == "p"
    assert str(props[1]) == "q"


def test_state_transition_and_valid_structure():
    p, q = Proposition.propositions("p", "q")
    props = {p, q}

    s1 = State("s1", {p})
    s2 = State("s2", {q})
    s3 = State("s3", {p, q})

    s1.make_transition(s2)
    s2.make_transition(s3)

    # transition set updated
    assert s2 in s1.next_states

    ks = KripkeStructure({s1}, props)
    assert ks.is_valid()


def test_invalid_label_not_in_propositions():
    p = Proposition.propositions("p")[0]
    props = {p}

    s1 = State("s1", {p})
    # label uses a proposition not present in the Kripke propositions set
    s2 = State("s2", {Proposition("r")})
    s1.make_transition(s2)

    ks = KripkeStructure({s1}, props)
    assert not ks.is_valid()


def test_unreachable_state_ignored_by_validation():
    p = Proposition.propositions("p")[0]
    props = {p}

    s1 = State("s1", {p})
    # unreachable state with invalid label
    unreachable = State("u", {Proposition("bad")})

    ks = KripkeStructure({s1}, props)
    # unreachable state's invalid labels should not affect validity
    assert ks.is_valid()


def test_proposition_factory_invalid_inputs():
    with pytest.raises(AssertionError):
        Proposition.propositions()

    with pytest.raises(AssertionError):
        Proposition.propositions(1, 2)


# Helper to run `is_valid` in a separate process with timeout to avoid hangs
import multiprocessing


def _worker_is_valid(q, ks):
    try:
        q.put(ks.is_valid())
    except Exception as e:
        q.put(e)


def run_is_valid_with_timeout(ks, timeout=5):
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_worker_is_valid, args=(q, ks))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutError("is_valid timed out")
    if q.empty():
        raise RuntimeError("No result returned from is_valid worker")
    res = q.get()
    if isinstance(res, Exception):
        raise res
    return res


def make_chain(n, prop):
    nodes = [State(f"s{i}", {prop}) for i in range(n)]
    for i in range(n - 1):
        nodes[i].make_transition(nodes[i + 1])
    return nodes


def test_large_chain_valid():
    p = Proposition.propositions("p")[0]
    props = {p}
    nodes = make_chain(1000, p)
    ks = KripkeStructure({nodes[0]}, props)
    assert run_is_valid_with_timeout(ks, timeout=5) is True


def test_large_chain_invalid_deep_label():
    p = Proposition.propositions("p")[0]
    props = {p}
    nodes = make_chain(1000, p)
    # make the last node invalid
    nodes[-1].labels = {Proposition("bad")}
    ks = KripkeStructure({nodes[0]}, props)
    assert run_is_valid_with_timeout(ks, timeout=5) is False


def test_large_cycle():
    p = Proposition.propositions("p")[0]
    props = {p}
    n = 1000
    nodes = [State(f"s{i}", {p}) for i in range(n)]
    for i in range(n - 1):
        nodes[i].make_transition(nodes[i + 1])
    nodes[-1].make_transition(nodes[0])
    ks = KripkeStructure({nodes[0]}, props)
    assert run_is_valid_with_timeout(ks, timeout=5) is True
