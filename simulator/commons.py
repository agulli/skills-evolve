"""The shared commons — append-only evidence ledger and the promotion
lifecycle: shared → proposed → Canon, with a human block/remove backstop.

Promotion is deliberately conservative and evidence-first (mirrors the
TELEMETRY.md lifecycle):
  • shared    — evidence is accumulating; no status.
  • proposed  — the Beta-posterior confirmation tail clears `promote_p` AND the
                evidence spans ≥ `min_orgs` independent orgs and ≥ `min_classes`
                use-case classes (per class). Independence is what defeats a
                single optimist or a sybil bloc.
  • canon     — a proposed skill that stays clear after further evidence.
  • blocked   — a human maintainer can remove/deny any skill (governance sits
                outside the automated loop). Used here to model the backstop.

Org-jackknife: a confirmation that collapses when any single org's evidence is
removed is not robust — this is what neutralizes a coordinated sybil org.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set

from .stats import beta_tail


@dataclass
class Ledger:
    # per (skill_idx, uclass): {org: [confirm_weight, refute_weight]}
    evidence: Dict[tuple, Dict[int, List[float]]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(lambda: [0.0, 0.0])))
    status: Dict[int, str] = field(default_factory=dict)          # skill_idx -> shared/proposed/canon
    blocked: Set[int] = field(default_factory=set)

    def record(self, org: int, skill_idx: int, uclass: str, c: float, r: float):
        cell = self.evidence[(skill_idx, uclass)][org]
        cell[0] += c
        cell[1] += r

    def _confirms_refutes(self, skill_idx: int, uclass: str, drop_org: int = None):
        c = r = 0.0
        orgs = set()
        for org, (cw, rw) in self.evidence[(skill_idx, uclass)].items():
            if org == drop_org:
                continue
            c += cw
            r += rw
            if cw > 0:
                orgs.add(org)
        return c, r, orgs

    def _class_promotable(self, skill_idx: int, uclass: str,
                          promote_p: float, min_orgs: int) -> bool:
        c, r, orgs = self._confirms_refutes(skill_idx, uclass)
        if len(orgs) < min_orgs:
            return False
        if beta_tail(c, r) < promote_p:
            return False
        # org-jackknife: must still clear if any single org is removed
        for org in list(orgs):
            cj, rj, oj = self._confirms_refutes(skill_idx, uclass, drop_org=org)
            if len(oj) < min_orgs - 1 or beta_tail(cj, rj) < promote_p:
                return False
        return True

    def tally(self, promote_p: float = 0.9, min_orgs: int = 3, min_classes: int = 2):
        """Recompute status for every skill with evidence."""
        skills = {sk for (sk, _cl) in self.evidence}
        for sk in skills:
            if sk in self.blocked:
                self.status[sk] = "blocked"
                continue
            good_classes = [cl for (s2, cl) in self.evidence if s2 == sk
                            and self._class_promotable(sk, cl, promote_p, min_orgs)]
            cur = self.status.get(sk, "shared")
            if len(good_classes) >= min_classes:
                # proposed on first qualification; canon once it has persisted
                self.status[sk] = "canon" if cur in ("proposed", "canon") else "proposed"
            else:
                if cur in ("proposed", "canon"):
                    self.status[sk] = "proposed"  # demote canon→proposed if support thins
                else:
                    self.status[sk] = "shared"

    def canon_by_class(self, promote_p: float = 0.9, min_orgs: int = 3) -> Dict[str, List[int]]:
        """Which skills a newcomer would adopt for each class from today's Canon."""
        out: Dict[str, List[int]] = defaultdict(list)
        for sk, st in self.status.items():
            if st != "canon" or sk in self.blocked:
                continue
            for (s2, cl) in self.evidence:
                if s2 == sk and self._class_promotable(sk, cl, promote_p, min_orgs):
                    out[cl].append(sk)
        return out

    def promoted(self) -> Set[int]:
        return {sk for sk, st in self.status.items() if st in ("proposed", "canon")
                and sk not in self.blocked}

    def block(self, skill_idx: int):
        """Human maintainer removes a skill from the Canon (governance backstop)."""
        self.blocked.add(skill_idx)
        self.status[skill_idx] = "blocked"
