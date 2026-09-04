"""LAYCAN — a freight *decision* engine for bulk cargo procurement into India.

Not a forecasting model. Dry bulk freight is near a random walk and the FFA
forward curve already prices it more efficiently than any model we could build,
so the value sits where forecast superiority is not required:

  * an optimal-stopping policy giving a daily reservation rate — fix or wait
  * hard physical feasibility — which vessel can actually load full at which port
  * instrument mix — spot vs trip charter vs COA on a cost-versus-tail-risk view
  * hedge sizing — with residual basis risk always reported

Two structural rules, enforced in ``laycan.core.guards``:
the language model may not emit a numeral, and no feature may be read from the
future.
"""

__version__ = "0.1.0"
