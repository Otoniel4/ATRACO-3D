using UnityEngine;
using UnityEngine.AI;

namespace Alarma.AI.CityLife
{
    [RequireComponent(typeof(NavMeshAgent))]
    public sealed class PedestrianMovement : MonoBehaviour, IPedestrianMotor
    {
        private NavMeshAgent agent;
        private readonly NavMeshPath path = new NavMeshPath();
        public float Speed => agent != null && agent.enabled && agent.isOnNavMesh ? agent.velocity.magnitude : 0f;
        public bool HasArrived => agent != null && agent.enabled && agent.isOnNavMesh && !agent.pathPending &&
            agent.pathStatus == NavMeshPathStatus.PathComplete && agent.remainingDistance <= agent.stoppingDistance + .08f;
        private void Awake() => agent = GetComponent<NavMeshAgent>();
        public bool Place(Vector3 position, float speed, int priority)
        {
            if (agent == null) agent = GetComponent<NavMeshAgent>();
            if (!NavMesh.SamplePosition(position, out NavMeshHit hit, .8f, NavMesh.AllAreas)) return false;
            transform.position = hit.position;
            agent.enabled = true; agent.speed = speed; agent.acceleration = 4f; agent.angularSpeed = 220f;
            agent.radius = .24f; agent.height = 1.8f; agent.stoppingDistance = .10f;
            agent.avoidancePriority = priority; agent.autoBraking = true;
            return agent.Warp(hit.position);
        }
        public bool MoveTo(CityPoint point)
        {
            if (agent == null || !agent.enabled || !agent.isOnNavMesh) return false;
            Vector3 target = new Vector3(point.X, point.Y, point.Z);
            if (!NavMesh.SamplePosition(target, out NavMeshHit hit, .55f, agent.areaMask)) return false;
            if (!agent.CalculatePath(hit.position, path) || path.status != NavMeshPathStatus.PathComplete) return false;
            agent.isStopped = false; return agent.SetPath(path);
        }
        public void Stop() { if (agent != null && agent.enabled && agent.isOnNavMesh) { agent.ResetPath(); agent.isStopped = true; } }
        public void Suspend() { Stop(); if (agent != null) agent.enabled = false; }
    }
}
