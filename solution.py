## Student Name: Salim Haddad
## Student ID: 219930270

"""
Task B: Event Registration with Waitlist

Implements an Event Registration system for a single event with fixed capacity:
- Register users until capacity is reached
- Extra users go to a FIFO waitlist
- Canceling a registered user promotes the earliest waitlisted user (if any)
- Prevent duplicate registrations (a user cannot be in the system more than once)
- Allow users to query their status
"""

from dataclasses import dataclass
from typing import List, Optional, Dict


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Deterministic ordering is required:
    - Registration order is the order users successfully register
    - Waitlist order is FIFO
    - Promotions are deterministic for identical operation sequences
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an int")
        if capacity < 0:
            raise ValueError("capacity must be >= 0")

        self._capacity: int = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []

        # Sets for fast membership checking
        self._reg_set = set()
        self._wait_set = set()

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists
        """
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a str")
        if user_id == "":
            raise ValueError("user_id must be non-empty")

        if user_id in self._reg_set or user_id in self._wait_set:
            raise DuplicateRequest(f"{user_id} is already registered or waitlisted")

        # If space available -> register
        if len(self._registered) < self._capacity:
            self._registered.append(user_id)
            self._reg_set.add(user_id)
            return UserStatus("registered")

        # Otherwise -> waitlist
        self._waitlist.append(user_id)
        self._wait_set.add(user_id)
        return UserStatus("waitlisted", len(self._waitlist))

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user
          - if waitlisted -> remove from waitlist
          - if not found -> raise NotFound
        """
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a str")
        if user_id == "":
            raise ValueError("user_id must be non-empty")

        # Registered user cancel
        if user_id in self._reg_set:
            self._registered.remove(user_id)
            self._reg_set.remove(user_id)

            # Promote earliest waitlisted user if possible
            if self._waitlist and len(self._registered) < self._capacity:
                promoted = self._waitlist.pop(0)
                self._wait_set.remove(promoted)

                self._registered.append(promoted)
                self._reg_set.add(promoted)
            return

        # Waitlisted user cancel
        if user_id in self._wait_set:
            self._waitlist.remove(user_id)
            self._wait_set.remove(user_id)
            return

        # User not found
        raise NotFound(f"{user_id} not found")

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a str")
        if user_id == "":
            raise ValueError("user_id must be non-empty")

        if user_id in self._reg_set:
            return UserStatus("registered")

        if user_id in self._wait_set:
            position = self._waitlist.index(user_id) + 1
            return UserStatus("waitlisted", position)

        return UserStatus("none")

    def snapshot(self) -> Dict[str, object]:
        """
        Return a deterministic snapshot of internal state.
        Useful for debugging/tests.
        """
        return {
            "capacity": self._capacity,
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
        }
