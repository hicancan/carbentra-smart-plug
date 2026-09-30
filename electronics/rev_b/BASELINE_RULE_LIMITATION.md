# Frozen EVT-A rule limitation

The EVT-A files remain unchanged for traceability. During CARBENTRA EVT-B review, a reproducible negative control demonstrated that JavaScript-style `NetName.startsWith(...)` expressions in KiCad custom rules did not enforce the intended net-prefix constraints. A generic native DRC count of zero therefore does not prove those particular domain rules were evaluated.

EVT-B integrated rules use supported `NetName == 'HOT_*'` wildcard comparisons with explicit symmetric conditions. Native negative controls and an independent all-layer projected-copper audit are retained under `integrated/validation/rule_controls/`. The modular B metering reference was corrected and rerun with zero violations and zero unconnected items. Controller rules use explicit net names; feedback uses explicit net classes and its independent negative control.

This note does not upgrade or requalify EVT-A. Neither revision is authorized for fabrication or energization by its digital check results. Manufacturing insulation, component tolerances, high-current heating, protection coordination and physical safety tests remain separate release gates.
