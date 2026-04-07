export type EffectType =
  | "github_write"
  | "github_branch_create"
  | "github_pr_create"
  | "verify_run"
  | "browser_check"
  | "deploy_mirror"
  | "deploy_live"
  | "rollback";

export interface ResourceScope {
  repo: string;
  branch?: string;
  path?: string;
}

export interface SideEffectRequest {
  effectId: string;
  effectType: EffectType;
  sourceEventId: string;
  resource: ResourceScope;
  payload: unknown;
  executionPolicy: {
    retry: number;
    timeoutSeconds: number;
    idempotent: boolean;
  };
}

export interface ExecutionResult {
  effectId: string;
  status: "success" | "failure" | "blocked";
  reason?: string;
  output?: unknown;
}

export interface EffectHandler {
  handle(request: SideEffectRequest): Promise<ExecutionResult>;
}

export type HandlerMap = Partial<Record<EffectType, EffectHandler>>;

export class SideEffectExecutor {
  constructor(private readonly handlers: HandlerMap) {}

  async execute(request: SideEffectRequest): Promise<ExecutionResult> {
    this.validate(request);

    if (request.effectType === "deploy_live") {
      return {
        effectId: request.effectId,
        status: "blocked",
        reason: "live_deploy_must_be_explicitly_authorized_by_guardrail",
      };
    }

    const handler = this.handlers[request.effectType];
    if (!handler) {
      return {
        effectId: request.effectId,
        status: "blocked",
        reason: "no_handler_registered_for_effect_type",
      };
    }

    return handler.handle(request);
  }

  private validate(request: SideEffectRequest): void {
    if (!request.effectId || !request.sourceEventId) {
      throw new Error("executor: invalid_effect_request");
    }

    if (request.executionPolicy.retry < 0 || request.executionPolicy.timeoutSeconds <= 0) {
      throw new Error("executor: invalid_execution_policy");
    }
  }
}

export class NoopHandler implements EffectHandler {
  async handle(request: SideEffectRequest): Promise<ExecutionResult> {
    return {
      effectId: request.effectId,
      status: "success",
      output: { handledBy: "NoopHandler", effectType: request.effectType },
    };
  }
}
