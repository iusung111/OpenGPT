export type SessionRole = "delivery" | "reliability" | "reviewer";

export type LeaseStatus = "active" | "expired" | "revoked";

export interface ResourceScope {
  repo: string;
  branch?: string;
  path?: string;
}

export interface Session {
  sessionId: string;
  role: SessionRole;
  templateVersion: string;
  createdAt: string;
  expiresAt: string;
}

export interface Lease {
  leaseId: string;
  sessionId: string;
  resource: ResourceScope;
  status: LeaseStatus;
  createdAt: string;
  expiresAt: string;
}

export interface SessionStore {
  getSession(sessionId: string): Promise<Session | null>;
  getLease(leaseId: string): Promise<Lease | null>;
  hasActiveLock(resource: ResourceScope, exceptLeaseId?: string): Promise<boolean>;
  saveLease(lease: Lease): Promise<void>;
}

export interface Clock {
  now(): Date;
}

export class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }
}

export class SessionManager {
  constructor(
    private readonly store: SessionStore,
    private readonly clock: Clock = new SystemClock(),
  ) {}

  async isValidLease(
    sessionId: string,
    leaseId: string,
    resource: ResourceScope,
  ): Promise<boolean> {
    const [session, lease] = await Promise.all([
      this.store.getSession(sessionId),
      this.store.getLease(leaseId),
    ]);

    if (!session || !lease) {
      return false;
    }

    if (lease.sessionId !== sessionId) {
      return false;
    }

    if (session.expiresAt <= this.clock.now().toISOString()) {
      return false;
    }

    if (lease.status !== "active" || lease.expiresAt <= this.clock.now().toISOString()) {
      return false;
    }

    return this.sameResource(lease.resource, resource);
  }

  async acquireLease(input: {
    leaseId: string;
    sessionId: string;
    resource: ResourceScope;
    ttlSeconds: number;
  }): Promise<Lease> {
    const session = await this.store.getSession(input.sessionId);
    if (!session) {
      throw new Error("session: session_not_found");
    }

    const locked = await this.store.hasActiveLock(input.resource);
    if (locked) {
      throw new Error("session: resource_already_locked");
    }

    const now = this.clock.now();
    const lease: Lease = {
      leaseId: input.leaseId,
      sessionId: input.sessionId,
      resource: input.resource,
      status: "active",
      createdAt: now.toISOString(),
      expiresAt: new Date(now.getTime() + input.ttlSeconds * 1000).toISOString(),
    };

    await this.store.saveLease(lease);
    return lease;
  }

  private sameResource(left: ResourceScope, right: ResourceScope): boolean {
    return (
      left.repo === right.repo &&
      (left.branch ?? "") === (right.branch ?? "") &&
      (left.path ?? "") === (right.path ?? "")
    );
  }
}
