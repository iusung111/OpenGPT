export interface ResourceScope {
  repo: string;
  branch?: string;
  path?: string;
}

export interface MissionEvent {
  eventId: string;
  commandId: string;
  type: string;
  status: string;
  reason?: string;
  resource: ResourceScope;
  createdAt: string;
}

export interface Session {
  sessionId: string;
  role: string;
  templateVersion: string;
  createdAt: string;
  expiresAt: string;
}

export interface Lease {
  leaseId: string;
  sessionId: string;
  resource: ResourceScope;
  status: string;
  createdAt: string;
  expiresAt: string;
}

export interface QueueItem {
  itemId: string;
  queue: string;
  priority: string;
  blocking: boolean;
  createdAt: string;
  payload: unknown;
}

export interface RuntimeStore {
  hasDedup(key: string): Promise<boolean>;
  hasConflict(key: string, resource: ResourceScope): Promise<boolean>;
  appendEvent(event: MissionEvent): Promise<void>;

  getSession(sessionId: string): Promise<Session | null>;
  getLease(leaseId: string): Promise<Lease | null>;
  hasActiveLock(resource: ResourceScope, exceptLeaseId?: string): Promise<boolean>;
  saveLease(lease: Lease): Promise<void>;

  list(queue: string): Promise<QueueItem[];
  enqueue(item: QueueItem): Promise<void>;
  dequeue(itemId: string): Promise<void>;
}

export class InMemoryRuntimeStore implements RuntimeStore {
  private readonly dedupKeys = new Set<string>();
  private readonly conflictKeys = new Map<string, ResourceScope>();
  private readonly events : MissionEvent[] = [];
  private readonly sessions = new Map<string, Session>();
  private readonly leases = new Map<string, Lease>();
  private readonly queues = new Map<string, QueueItem[]>();

  async hasDedup(key: string): Promise<boolean> {
    return this.dedupKeys.has(key);
  }

  async hasConflict(key: string, resource: ResourceScope): Promise<boolean> {
    const existing = this.conflictKeys.get(key);
    if (!existing) {
      return false;
    }

    return this.sameResource(existing, resource);
  }

  async appendEvent(event: MissionEvent): Promise<void> {
    this.events.push(event);
    this.dedupKeys.add(event.commandId);
    if (event.resource.repo) {
      this.conflictKeys.set(event.commandId, event.resource);
    }
  }

  async getSession(sessionId: string): Promise<Session | null> {
    return this.sessions.get(sessionId) ?? null;
  }

  async getLease(leaseId: string): Promise<Lease | null> {
    return this.leases.get(leaseId) ?? null;
  }

  async hasActiveLock(resource: ResourceScope, exceptLeaseId?: string): Promise<boolean> {
    for (const lease of this.leases.values()) {
      if (exceptLeaseId && lease.leaseId === exceptLeaseId) {
        continue;
      }
      if (lease.status !== "active") {
        continue;
      }
      if (this.sameResource(lease.resource, resource)) {
        return true;
      }
    }

    return false;
  }

  async saveLease(lease: Lease): Promise<void> {
    this.leases.set(lease.leaseId, lease);
  }

  async list(queue: string): Promise<QueueItem[]> {
    return this.queues.get(queue) ?? [];
  }

  async enqueue(item: QueueItem): Promise<void> {
    const existing = this.queues.get(item.queue) ?? [];
    existing.push(item);
    this.queues.set(item.queue, existing);
  }

  async dequeue(itemId: string): Promise<void> {
    for (const [queue, items] of this.queues.entries()) {
      this.queues.set(queue, items.filter(item => item.itemId !== itemId));
    }
  }

  seedSession(session: Session): void {
    this.sessions.set(session.sessionId, session);
  }

  getEvents(): MissionEvent[] {
    return this.events.slice();
  }

  private sameResource(left: ResourceScope, right: ResourceScope): boolean {
    return (
      left.repo === right.repo &&
      (left.branch ?? "") === (right.branch ?? "") &&
      (left.path ?? "") === (right.path ?? "")
    );
  }
}
