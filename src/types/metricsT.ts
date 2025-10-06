export interface Disk {
  device?: string;
  mountpoint?: string;
  used?: number;
  total?: number;
  used_pct?: number;
}

export interface ProcessInfo {
  pid?: number;
  name?: string;
  cpu_percent?: number;
  memory_percent?: number;
}

export interface Metrics {
  timestamp?: string;
  hw?: Record<string, unknown>;
  cpu?: {
    physical_cores?: number;
    total_cores?: number;
    usage_pct: number[];
  };
  memory?: {
    total?: number;
    used?: number;
    used_pct?: number;
  };
  disks?: Disk[];
  top_processes?: ProcessInfo[];
  drivers?: Record<string, unknown>;
  [key: string]: unknown;
}
