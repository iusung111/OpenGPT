export type QueueType =
  | "task"
  | "review"
  | "proposal"
  | "conflict"
  | "deploy";

export type QueuePriority = "P0" | "P1" | "P2" | "P3" | "P4" | "P5";

export interface QueueItem {
  itemId: string;
  queue: QueueType;
  priority: QueuePriority;
  blocking: boolean;
  createdAt: string;
  payload: unknown;
}

export interface QueueStore {
  list(queue: QueueType): Promise<QueueItem[]>;
  enqueue(item: QueueItem): Promise<void>;
  dequeue(itemId: string): Promise<void>;
}

export class QueueManager {
  constructor(private readonly store: QueueStore) {}

  async put(item: QueueItem): Promise<void> {
    await this.store.enqueue(item);
  }

  async next(queue: QueueType): Promise<QueueItem | null> {
    const items = await this.store.list(queue);
    if (items.length === 0) {
      return null;
    }

    const sorted = items
      .slice()
      .sort((left, right) => this.compare(left, right));

    return sorted[0];
  }

  async consume(queue: QueueType): Promise<QueueItem | null> {
    const nextItem = await this.next(queue);
    if (!nextItem) {
      return null;
    }

    await this.store.dequeue(nextItem.itemId);
    return nextItem;
  }

  private compare(left: QueueItem, right: QueueItem): number {
    if (left.blocking !== right.blocking) {
      return left.blocking ? -1 : 1;
    }

    const priorityDiff = this.priorityWeight(left.priority) - this.priorityWeight(right.priority);
    if (priorityDiff !== 0) {
      return priorityDiff;
    }

    return new Date(left.createdAt).getTime() - new Date(right.createdAt).getTime();
  }

  private priorityWeight(priority: QueuePriority): number {
    const order: Record<QueuePriority, number> = {
      P0: 0,
      P1: 1,
      P2: 2,
      P3: 3,
      P4: 4,
      P5: 5,
    };

    return order[priority];
  }
}
