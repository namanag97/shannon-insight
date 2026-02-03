// High complexity TypeScript - many concerns, deep nesting
import * as fs from "fs";
import * as path from "path";
import * as crypto from "crypto";
import { promisify } from "util";

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);

interface Config {
  database: DatabaseConfig;
  cache: CacheConfig;
  security: SecurityConfig;
  api: APIConfig;
  logging: LoggingConfig;
  features: FeatureFlags;
}

interface DatabaseConfig {
  host: string;
  port: number;
  username: string;
  password: string;
  database: string;
  pool: PoolConfig;
  ssl: SSLConfig;
}

interface PoolConfig {
  min: number;
  max: number;
  idle: number;
  acquire: number;
  evict: number;
}

interface SSLConfig {
  enabled: boolean;
  caPath?: string;
  certPath?: string;
  keyPath?: string;
  rejectUnauthorized: boolean;
}

interface CacheConfig {
  enabled: boolean;
  type: "redis" | "memory" | "memcached";
  host: string;
  port: number;
  ttl: number;
  maxSize: number;
  strategy: "lru" | "lfu" | "fifo";
}

interface SecurityConfig {
  jwtSecret: string;
  jwtExpiration: number;
  bcryptRounds: number;
  rateLimiting: RateLimitConfig;
  cors: CORSConfig;
  csrf: CSRFConfig;
}

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  skipSuccessfulRequests: boolean;
  skipFailedRequests: boolean;
}

interface CORSConfig {
  enabled: boolean;
  origin: string | string[] | boolean;
  credentials: boolean;
  methods: string[];
  allowedHeaders: string[];
  exposedHeaders: string[];
  maxAge: number;
}

interface CSRFConfig {
  enabled: boolean;
  secret: string;
  saltLength: number;
  cookieOptions: CookieOptions;
}

interface CookieOptions {
  httpOnly: boolean;
  secure: boolean;
  sameSite: "strict" | "lax" | "none";
  maxAge: number;
  domain?: string;
  path?: string;
}

interface APIConfig {
  port: number;
  host: string;
  timeout: number;
  bodyParser: BodyParserConfig;
  compression: CompressionConfig;
  rateLimiting: RateLimitConfig;
}

interface BodyParserConfig {
  json: {
    limit: string;
    strict: boolean;
    inflate: boolean;
  };
  urlencoded: {
    limit: string;
    extended: boolean;
    inflate: boolean;
  };
}

interface CompressionConfig {
  enabled: boolean;
  level: number;
  threshold: number;
  chunkSize: number;
  memLevel: number;
  strategy: "fixed" | "dynamic";
}

interface LoggingConfig {
  level: "debug" | "info" | "warn" | "error";
  format: "json" | "text";
  transports: TransportConfig[];
  exceptions: ExceptionConfig;
}

interface TransportConfig {
  type: "console" | "file" | "http";
  options: any;
}

interface ExceptionConfig {
  enabled: boolean;
  exitOnError: boolean;
  handleExceptions: boolean;
  handleRejections: boolean;
}

interface FeatureFlags {
  newUserFlow: boolean;
  advancedSearch: boolean;
  analytics: boolean;
  betaFeatures: boolean;
  experimentalFeatures: boolean[];
}

class ComplexConfigManager {
  private config: Config | null = null;
  private cache: Map<string, any> = new Map();
  private watchers: Map<string, Array<(val: any) => void>> = new Map();
  private validators: Array<(config: Config) => boolean> = [];
  private transformers: Array<(config: Config) => Config> = [];
  private middlewares: Array<(key: string, value: any, config: Config) => any> = [];
  private hooks: Map<string, Array<(config: Config) => void>> = new Map();
  private initialized: boolean = false;

  constructor(private configPath: string) {
    this.initializeValidators();
    this.initializeTransformers();
    this.initializeMiddlewares();
  }

  async load(): Promise<Config> {
    if (this.config && this.initialized) {
      return this.config;
    }

    try {
      const content = await readFile(this.configPath, "utf-8");
      this.config = this.parseConfig(content);
      await this.processConfig(this.config);
      this.initialized = true;
      this.notifyWatchers("config:loaded", this.config);
      return this.config;
    } catch (error) {
      throw new Error(`Failed to load config: ${error}`);
    }
  }

  private parseConfig(content: string): Config {
    try {
      return JSON.parse(content);
    } catch (error) {
      if (this.isYAML(content)) {
        return this.parseYAML(content);
      }
      if (this.isTOML(content)) {
        return this.parseTOML(content);
      }
      throw new Error("Unsupported config format");
    }
  }

  private isYAML(content: string): boolean {
    return /^[\s\S]*?:[\s\S]*?\n/.test(content) || /^---\s*\n/.test(content);
  }

  private isTOML(content: string): boolean {
    return /^\[[a-zA-Z0-9_\-\.]+\]/.test(content) || /^[a-zA-Z0-9_\-\.]+\s*=\s*/.test(content);
  }

  private parseYAML(content: string): Config {
    const lines = content.split("\n");
    const config: any = {};
    let currentSection: any = config;
    const stack: Array<{ section: any; indent: number }> = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line || line.startsWith("#")) {
        continue;
      }

      const sectionMatch = line.match(/^([a-zA-Z][a-zA-Z0-9_]*)\s*:/);
      if (sectionMatch) {
        const indent = lines[i].search(/\S/);
        while (stack.length > 0 && stack[stack.length - 1].indent >= indent) {
          stack.pop();
        }
        currentSection = stack.length > 0 ? stack[stack.length - 1].section : config;
        currentSection[sectionMatch[1]] = {};
        stack.push({ section: currentSection[sectionMatch[1]], indent });
        currentSection = currentSection[sectionMatch[1]];
        continue;
      }

      const kvMatch = line.match(/^([a-zA-Z][a-zA-Z0-9_]*)\s*:\s*(.*)$/);
      if (kvMatch) {
        let value = kvMatch[2].trim();
        if (value.startsWith('"') && value.endsWith('"')) {
          value = value.slice(1, -1);
        } else if (value === "true" || value === "false") {
          value = value === "true";
        } else if (!isNaN(Number(value))) {
          value = Number(value);
        } else if (value.startsWith("[")) {
          value = this.parseArray(value);
        }
        currentSection[kvMatch[1]] = value;
      }

      const arrayItemMatch = line.match(/^-\s*(.*)$/);
      if (arrayItemMatch && Array.isArray(currentSection)) {
        let value = arrayItemMatch[1].trim();
        if (value.startsWith('"') && value.endsWith('"')) {
          value = value.slice(1, -1);
        }
        currentSection.push(value);
      }
    }

    return this.validateAndNormalize(config);
  }

  private parseTOML(content: string): Config {
    const lines = content.split("\n");
    const config: any = {};
    let currentSection: any = config;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line || line.startsWith("#")) {
        continue;
      }

      const sectionMatch = line.match(/^\[([a-zA-Z0-9_\.-]+)\]$/);
      if (sectionMatch) {
        const parts = sectionMatch[1].split(".");
        currentSection = config;
        for (let j = 0; j < parts.length - 1; j++) {
          if (!currentSection[parts[j]]) {
            currentSection[parts[j]] = {};
          }
          currentSection = currentSection[parts[j]];
        }
        if (!currentSection[parts[parts.length - 1]]) {
          currentSection[parts[parts.length - 1]] = {};
        }
        currentSection = currentSection[parts[parts.length - 1]];
        continue;
      }

      const kvMatch = line.match(/^([a-zA-Z0-9_\-\.]+)\s*=\s*(.*)$/);
      if (kvMatch) {
        let value = kvMatch[2].trim();
        if (value.startsWith('"') && value.endsWith('"')) {
          value = value.slice(1, -1);
        } else if (value === "true" || value === "false") {
          value = value === "true";
        } else if (!isNaN(Number(value))) {
          value = Number(value);
        } else if (value.startsWith("[")) {
          value = this.parseArray(value);
        }
        currentSection[kvMatch[1]] = value;
      }
    }

    return this.validateAndNormalize(config);
  }

  private parseArray(value: string): any[] {
    const content = value.slice(1, -1).trim();
    if (!content) {
      return [];
    }

    const items: any[] = [];
    const parts = content.split(",");
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
        items.push(trimmed.slice(1, -1));
      } else if (trimmed === "true" || trimmed === "false") {
        items.push(trimmed === "true");
      } else if (!isNaN(Number(trimmed))) {
        items.push(Number(trimmed));
      } else {
        items.push(trimmed);
      }
    }

    return items;
  }

  private validateAndNormalize(config: any): Config {
    const normalized = this.applyDefaults(config);
    for (const validator of this.validators) {
      if (!validator(normalized)) {
        throw new Error("Config validation failed");
      }
    }
    return normalized;
  }

  private applyDefaults(config: any): Config {
    return {
      database: {
        host: config.database?.host || "localhost",
        port: config.database?.port || 5432,
        username: config.database?.username || "user",
        password: config.database?.password || "",
        database: config.database?.database || "app",
        pool: {
          min: config.database?.pool?.min || 2,
          max: config.database?.pool?.max || 10,
          idle: config.database?.pool?.idle || 10000,
          acquire: config.database?.pool?.acquire || 60000,
          evict: config.database?.pool?.evict || 60000,
        },
        ssl: {
          enabled: config.database?.ssl?.enabled || false,
          caPath: config.database?.ssl?.caPath,
          certPath: config.database?.ssl?.certPath,
          keyPath: config.database?.ssl?.keyPath,
          rejectUnauthorized: config.database?.ssl?.rejectUnauthorized ?? true,
        },
      },
      cache: {
        enabled: config.cache?.enabled ?? true,
        type: config.cache?.type || "memory",
        host: config.cache?.host || "localhost",
        port: config.cache?.port || 6379,
        ttl: config.cache?.ttl || 3600,
        maxSize: config.cache?.maxSize || 1000,
        strategy: config.cache?.strategy || "lru",
      },
      security: {
        jwtSecret: config.security?.jwtSecret || this.generateSecret(),
        jwtExpiration: config.security?.jwtExpiration || 3600,
        bcryptRounds: config.security?.bcryptRounds || 10,
        rateLimiting: {
          windowMs: config.security?.rateLimiting?.windowMs || 900000,
          maxRequests: config.security?.rateLimiting?.maxRequests || 100,
          skipSuccessfulRequests: config.security?.rateLimiting?.skipSuccessfulRequests ?? false,
          skipFailedRequests: config.security?.rateLimiting?.skipFailedRequests ?? false,
        },
        cors: {
          enabled: config.security?.cors?.enabled ?? true,
          origin: config.security?.cors?.origin || "*",
          credentials: config.security?.cors?.credentials || true,
          methods: config.security?.cors?.methods || ["GET", "POST", "PUT", "DELETE"],
          allowedHeaders: config.security?.cors?.allowedHeaders || ["Content-Type", "Authorization"],
          exposedHeaders: config.security?.cors?.exposedHeaders || [],
          maxAge: config.security?.cors?.maxAge || 86400,
        },
        csrf: {
          enabled: config.security?.csrf?.enabled ?? true,
          secret: config.security?.csrf?.secret || this.generateSecret(),
          saltLength: config.security?.csrf?.saltLength || 8,
          cookieOptions: {
            httpOnly: config.security?.csrf?.cookieOptions?.httpOnly ?? true,
            secure: config.security?.csrf?.cookieOptions?.secure ?? true,
            sameSite: config.security?.csrf?.cookieOptions?.sameSite || "strict",
            maxAge: config.security?.csrf?.cookieOptions?.maxAge || 86400000,
            domain: config.security?.csrf?.cookieOptions?.domain,
            path: config.security?.csrf?.cookieOptions?.path || "/",
          },
        },
      },
      api: {
        port: config.api?.port || 3000,
        host: config.api?.host || "0.0.0.0",
        timeout: config.api?.timeout || 30000,
        bodyParser: {
          json: {
            limit: config.api?.bodyParser?.json?.limit || "10mb",
            strict: config.api?.bodyParser?.json?.strict ?? true,
            inflate: config.api?.bodyParser?.json?.inflate ?? true,
          },
          urlencoded: {
            limit: config.api?.bodyParser?.urlencoded?.limit || "10mb",
            extended: config.api?.bodyParser?.urlencoded?.extended ?? true,
            inflate: config.api?.bodyParser?.urlencoded?.inflate ?? true,
          },
        },
        compression: {
          enabled: config.api?.compression?.enabled ?? true,
          level: config.api?.compression?.level || 6,
          threshold: config.api?.compression?.threshold || 1024,
          chunkSize: config.api?.compression?.chunkSize || 16384,
          memLevel: config.api?.compression?.memLevel || 8,
          strategy: config.api?.compression?.strategy || "dynamic",
        },
        rateLimiting: {
          windowMs: config.api?.rateLimiting?.windowMs || 900000,
          maxRequests: config.api?.rateLimiting?.maxRequests || 100,
          skipSuccessfulRequests: config.api?.rateLimiting?.skipSuccessfulRequests ?? false,
          skipFailedRequests: config.api?.rateLimiting?.skipFailedRequests ?? false,
        },
      },
      logging: {
        level: config.logging?.level || "info",
        format: config.logging?.format || "json",
        transports: config.logging?.transports || [
          { type: "console", options: {} },
        ],
        exceptions: {
          enabled: config.logging?.exceptions?.enabled ?? true,
          exitOnError: config.logging?.exceptions?.exitOnError ?? false,
          handleExceptions: config.logging?.exceptions?.handleExceptions ?? true,
          handleRejections: config.logging?.exceptions?.handleRejections ?? true,
        },
      },
      features: {
        newUserFlow: config.features?.newUserFlow ?? true,
        advancedSearch: config.features?.advancedSearch ?? true,
        analytics: config.features?.analytics ?? true,
        betaFeatures: config.features?.betaFeatures ?? false,
        experimentalFeatures: config.features?.experimentalFeatures || [],
      },
    };
  }

  private generateSecret(): string {
    return crypto.randomBytes(32).toString("hex");
  }

  private async processConfig(config: Config): Promise<void> {
    for (const transformer of this.transformers) {
      this.config = transformer(this.config || config);
    }

    await this.resolveEnvVars(this.config);
    await this.validatePaths(this.config);
    await this.runHooks("config:processed", this.config);
  }

  private async resolveEnvVars(config: Config): Promise<void> {
    const envMappings: Record<string, string> = {
      "database.host": "DB_HOST",
      "database.port": "DB_PORT",
      "database.username": "DB_USER",
      "database.password": "DB_PASSWORD",
      "database.database": "DB_NAME",
      "security.jwtSecret": "JWT_SECRET",
      "api.port": "PORT",
    };

    for (const [path, envVar] of Object.entries(envMappings)) {
      const value = process.env[envVar];
      if (value) {
        this.setNestedValue(config, path, value);
      }
    }
  }

  private setNestedValue(obj: any, path: string, value: any): void {
    const parts = path.split(".");
    let current = obj;
    for (let i = 0; i < parts.length - 1; i++) {
      if (!current[parts[i]]) {
        current[parts[i]] = {};
      }
      current = current[parts[i]];
    }
    current[parts[parts.length - 1]] = value;
  }

  private async validatePaths(config: Config): Promise<void> {
    const pathsToCheck = [
      config.database.ssl?.caPath,
      config.database.ssl?.certPath,
      config.database.ssl?.keyPath,
    ];

    for (const filePath of pathsToCheck) {
      if (filePath) {
        const exists = await this.pathExists(filePath);
        if (!exists) {
          throw new Error(`Path does not exist: ${filePath}`);
        }
      }
    }
  }

  private async pathExists(filePath: string): Promise<boolean> {
    try {
      await promisify(fs.stat)(filePath);
      return true;
    } catch {
      return false;
    }
  }

  private initializeValidators(): void {
    this.validators.push((config) => {
      return !!config && !!config.database && !!config.security;
    });

    this.validators.push((config) => {
      return config.security.jwtSecret.length >= 32;
    });

    this.validators.push((config) => {
      return config.api.port > 0 && config.api.port < 65536;
    });
  }

  private initializeTransformers(): void {
    this.transformers.push((config) => {
      if (config.security.jwtSecret === "CHANGE_ME") {
        console.warn("Using default JWT secret, please change in production");
      }
      return config;
    });
  }

  private initializeMiddlewares(): void {
    this.middlewares.push((key, value, config) => {
      if (typeof value === "string" && value.startsWith("env:")) {
        const envVar = value.slice(4);
        return process.env[envVar] || value;
      }
      return value;
    });

    this.middlewares.push((key, value) => {
      if (typeof value === "string" && value.includes("${")) {
        return this.interpolate(value);
      }
      return value;
    });
  }

  private interpolate(value: string): string {
    return value.replace(/\$\{([^}]+)\}/g, (match, varName) => {
      const nestedValue = this.getNestedValue(this.config || {} as any, varName);
      return nestedValue !== undefined ? String(nestedValue) : match;
    });
  }

  private getNestedValue(obj: any, path: string): any {
    const parts = path.split(".");
    let current = obj;
    for (const part of parts) {
      if (current && current[part] !== undefined) {
        current = current[part];
      } else {
        return undefined;
      }
    }
    return current;
  }

  watch(key: string, callback: (val: any) => void): void {
    if (!this.watchers.has(key)) {
      this.watchers.set(key, []);
    }
    this.watchers.get(key)!.push(callback);
  }

  unwatch(key: string, callback: (val: any) => void): void {
    const callbacks = this.watchers.get(key);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private notifyWatchers(key: string, value: any): void {
    const callbacks = this.watchers.get(key);
    if (callbacks) {
      for (const callback of callbacks) {
        callback(value);
      }
    }
  }

  addHook(name: string, hook: (config: Config) => void): void {
    if (!this.hooks.has(name)) {
      this.hooks.set(name, []);
    }
    this.hooks.get(name)!.push(hook);
  }

  removeHook(name: string, hook: (config: Config) => void): void {
    const hooks = this.hooks.get(name);
    if (hooks) {
      const index = hooks.indexOf(hook);
      if (index > -1) {
        hooks.splice(index, 1);
      }
    }
  }

  private async runHooks(name: string, config: Config): Promise<void> {
    const hooks = this.hooks.get(name);
    if (hooks) {
      for (const hook of hooks) {
        await Promise.resolve(hook(config));
      }
    }
  }

  async save(config: Config): Promise<void> {
    const content = JSON.stringify(config, null, 2);
    await writeFile(this.configPath, content, "utf-8");
    this.config = config;
    this.notifyWatchers("config:saved", config);
  }

  get<K extends keyof Config>(key: K): Config[K] {
    return (this.config || {} as any)[key];
  }

  async reload(): Promise<Config> {
    this.initialized = false;
    return this.load();
  }
}

export { ComplexConfigManager, Config };
