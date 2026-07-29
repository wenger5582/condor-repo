services:
    - type: web
    name: condor-api
    env: docker
    plan: free
    healthCheckPath: /api/health
