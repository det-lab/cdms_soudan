# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: cdms
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path

from scdms_soudan_spec import complete_test_file, soudan

# %%
# Build the complete test file
built_complete_test_file = soudan.build(complete_test_file)

# Write the built file to a binary file
output_path = Path("minimal_sample.soudan")
output_path.write_bytes(built_complete_test_file)

print(f"Wrote {output_path} ({output_path.stat().st_size} bytes)")

