# "Clean machine" definition for the onboarding proof (runbook Phase 4).
#
# The runbook defines a clean machine as one with no prior copy of the repo, no
# language runtime from this project, and no cached credential. This image is
# that machine, stated rather than assumed:
#
#   present : the OS baseline a fresh developer laptop has — git and curl
#   absent  : Python, uv, mise, and any agency-agents state
#
# Pinning the baseline is what makes before/after runs comparable: the only
# variable between two runs is the documented path, never the image.
FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# No Python, no uv, no mise: the project's runtime is installed by the
# documented path, or it is friction the friction inventory records.
WORKDIR /work
