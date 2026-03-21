from lum_pe.packs.registry import PackRegistry
from lum_pe.packs import impl

REGISTRY = PackRegistry()
REGISTRY.register("GENERIC_v1", impl.GENERIC_v1)
REGISTRY.register("FORM_GENERAL_v1", impl.FORM_GENERAL_v1)
REGISTRY.register("NAT_GENERAL_v1", impl.NAT_GENERAL_v1)
REGISTRY.register("SOC_DiD_v3", impl.SOC_DiD_v3)
REGISTRY.register("SOC_IV_v2", impl.SOC_IV_v2)
REGISTRY.register("ENG_TEST_v1", impl.ENG_TEST_v1)
