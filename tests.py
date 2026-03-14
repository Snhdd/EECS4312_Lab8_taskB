import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


# Covers C3, C6, AC3
def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


# Covers C1, C3, C5, AC1, AC4
def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


# Covers C2, AC2
def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


# Covers C1, C6, AC8
def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


# Covers C3, C8, AC7
def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")


#################################################################################
# Additional tests to cover more edge cases
#################################################################################

# Covers C1, C5, AC1, AC4
def test_multiple_cancellations_promote_multiple_waitlisted_in_order():
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")  # waitlisted
    er.register("u4")  # waitlisted

    er.cancel("u1")  # promotes u3
    er.cancel("u2")  # promotes u4

    snap = er.snapshot()
    assert snap["registered"] == ["u3", "u4"]
    assert snap["waitlist"] == []


# Covers C6, C7, AC5
def test_status_none_for_user_not_in_system():
    er = EventRegistration(capacity=1)
    assert er.status("ghost") == UserStatus("none")


# Covers C4, AC6
def test_cancel_registered_with_empty_waitlist_leaves_open_slot():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.cancel("u1")

    snap = er.snapshot()
    assert snap["registered"] == []
    assert snap["waitlist"] == []


# Covers C7, AC5
def test_user_can_reregister_after_canceling():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.cancel("u1")

    # should be allowed again
    assert er.register("u1") == UserStatus("registered")


# Covers C4, AC6
def test_cancel_missing_user_raises_notfound():
    er = EventRegistration(capacity=1)
    with pytest.raises(NotFound):
        er.cancel("missing-user")
