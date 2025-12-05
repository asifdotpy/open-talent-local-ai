#!/bin/bash
# scripts/rollback.sh

SUBMODULE=$1
TARGET_VERSION=$2

echo "Rolling back $SUBMODULE to $TARGET_VERSION"

# Stop current deployment
kubectl scale deployment $SUBMODULE --replicas=0

# Deploy previous version
kubectl set image deployment/$SUBMODULE app=talent-ai/$SUBMODULE:$TARGET_VERSION

# Scale back up
kubectl scale deployment $SUBMODULE --replicas=3

# Verify health
kubectl rollout status deployment/$SUBMODULE

echo "Rollback completed for $SUBMODULE"