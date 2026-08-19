(() => {
  "use strict";

  const CARD_TAG = "tessie-drive-stats-card";
  const CARD_TYPE = `custom:${CARD_TAG}`;
  const DOMAIN = "tessie_drive_stats";

  const VIEWS = [
    ["overview", "Overview"],
    ["drive", "Drive"],
    ["efficiency", "Efficiency"],
    ["charging", "Charging"],
    ["charging_economics", "Charging Economics"],
    ["battery", "Battery"],
    ["lifetime", "Lifetime"],
    ["idle", "Idle & Vampire"],
  ];

  const PERIODS = [
    ["today", "Today"],
    ["this_week", "This Week"],
    ["this_month", "This Month"],
    ["this_year", "This Year"],
  ];

  const LAYOUTS = [
    ["auto", "Auto"],
    ["compact", "Compact"],
    ["wide", "Wide"],
  ];

  const CARD_KEYS = [
    "vehicle_status",
    "connection_status",
    "battery_level_current",
    "battery_range_current",
    "ideal_battery_range_current",
    "charging_state_current",
    "charger_power_current",
    "charge_rate_current",
    "charge_limit",
    "time_to_full_charge",
    "outside_temperature_current",
    "miles_today",
    "miles_this_week",
    "miles_this_month",
    "miles_this_year",
    "drive_time_today",
    "drive_time_this_week",
    "drive_time_this_month",
    "drive_time_this_year",
    "energy_today",
    "energy_this_week",
    "energy_this_month",
    "energy_this_year",
    "efficiency_today",
    "efficiency_this_week",
    "efficiency_this_month",
    "efficiency_this_year",
    "estimated_driving_cost_today",
    "estimated_driving_cost_this_week",
    "estimated_driving_cost_this_month",
    "estimated_driving_cost_this_year",
    "estimated_drive_cost_per_mile_today",
    "estimated_drive_cost_per_mile_this_week",
    "estimated_drive_cost_per_mile_this_month",
    "estimated_drive_cost_per_mile_this_year",
    "last_drive_miles",
    "last_drive_time",
    "last_drive_efficiency",
    "last_drive_battery_used",
    "last_drive_average_speed",
    "last_drive_max_speed",
    "last_drive_outside_temperature",
    "last_drive_inside_temperature",
    "last_drive_autopilot_fsd_miles",
    "last_drive_efficiency_30_day_average",
    "last_drive_efficiency_vs_30_day",
    "last_drive_similar_temperature_efficiency",
    "last_drive_efficiency_vs_similar_temperature",
    "last_drive_similar_speed_efficiency",
    "last_drive_efficiency_vs_similar_speed",
    "last_drive_efficiency_percentile",
    "last_drive_temperature_band",
    "last_drive_speed_band",
    "last_drive_efficiency_context",
    "last_drive_unusually_inefficient",
    "last_charge_cost",
    "last_charge_energy_added",
    "last_charge_location",
    "last_supercharger_cost",
    "last_supercharger_energy_added",
    "last_supercharger_location",
    "last_charge_efficiency",
    "last_charge_loss",
    "last_charge_cost_per_kwh",
    "last_supercharger_cost_per_kwh",
    "charging_efficiency_today",
    "charging_efficiency_this_week",
    "charging_efficiency_this_month",
    "charging_efficiency_this_year",
    "charging_loss_today",
    "charging_loss_this_week",
    "charging_loss_this_month",
    "charging_loss_this_year",
    "average_charging_cost_per_kwh_today",
    "average_charging_cost_per_kwh_this_week",
    "average_charging_cost_per_kwh_this_month",
    "average_charging_cost_per_kwh_this_year",
    "charging_cost_coverage_today",
    "charging_cost_coverage_this_week",
    "charging_cost_coverage_this_month",
    "charging_cost_coverage_this_year",
    "battery_health",
    "battery_degradation",
    "battery_capacity",
    "battery_original_capacity",
    "battery_max_range",
    "battery_max_ideal_range",
    "battery_module_temp_min",
    "battery_module_temp_max",
    "battery_module_temp_spread",
    "battery_capacity_change_30_days",
    "battery_max_range_change_30_days",
    "recorded_lifetime_miles",
    "recorded_lifetime_drives",
    "recorded_lifetime_drive_time",
    "recorded_lifetime_drive_energy",
    "recorded_lifetime_efficiency",
    "recorded_lifetime_ap_fsd_miles",
    "recorded_lifetime_ap_fsd_share",
    "recorded_lifetime_charge_sessions",
    "recorded_lifetime_charge_energy_added",
    "recorded_lifetime_charge_cost",
    "recorded_lifetime_idle_energy",
    "recorded_lifetime_battery_measurements",
    "recorded_lifetime_capacity_change",
    "recorded_lifetime_data_since",
    "recorded_lifetime_supercharger_average_cost_per_kwh",
    "recorded_lifetime_non_supercharger_average_cost_per_kwh",
    "recorded_lifetime_supercharger_cost_premium",
    "idle_sessions_today",
    "idle_sessions_this_week",
    "idle_sessions_this_month",
    "idle_sessions_this_year",
    "idle_time_today",
    "idle_time_this_week",
    "idle_time_this_month",
    "idle_time_this_year",
    "idle_energy_today",
    "idle_energy_this_week",
    "idle_energy_this_month",
    "idle_energy_this_year",
    "idle_battery_used_today",
    "idle_battery_used_this_week",
    "idle_battery_used_this_month",
    "idle_battery_used_this_year",
    "idle_sentry_time_today",
    "idle_sentry_time_this_week",
    "idle_sentry_time_this_month",
    "idle_sentry_time_this_year",
    "idle_climate_time_today",
    "idle_climate_time_this_week",
    "idle_climate_time_this_month",
    "idle_climate_time_this_year",
    "last_idle_time",
    "last_idle_energy",
    "last_idle_battery_used",
    "last_idle_sentry_share",
    "last_idle_climate_share",
    "last_idle_location",
  ];

  const SORTED_KEYS = [...CARD_KEYS].sort((a, b) => b.length - a.length);
  const BINARY_KEYS = new Set(["last_drive_unusually_inefficient"]);
  const VIEW_VALUES = new Set(VIEWS.map(([value]) => value));
  const PERIOD_VALUES = new Set(PERIODS.map(([value]) => value));
  const LAYOUT_VALUES = new Set(LAYOUTS.map(([value]) => value));

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function titleCase(value) {
    return String(value ?? "—")
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function optionList(options) {
    return options.map(([value, label]) => ({ value, label }));
  }

  class TessieDriveStatsCard extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._config = null;
      this._hass = null;
      this._entityMap = new Map();
      this._resolvedConfigEntry = null;
      this._resolvingConfigEntry = null;
      this._renderQueued = false;
    }

    static getStubConfig() {
      return {
        view: "overview",
        layout: "auto",
        period: "this_month",
        show_header: true,
      };
    }

    static getConfigForm() {
      return {
        schema: [
          {
            name: "config_entry",
            selector: {
              config_entry: {
                integration: DOMAIN,
              },
            },
          },
          {
            name: "view",
            selector: {
              select: {
                options: optionList(VIEWS),
                mode: "dropdown",
              },
            },
          },
          {
            name: "layout",
            selector: {
              select: {
                options: optionList(LAYOUTS),
                mode: "dropdown",
              },
            },
          },
          {
            name: "period",
            selector: {
              select: {
                options: optionList(PERIODS),
                mode: "dropdown",
              },
            },
          },
          {
            name: "title",
            selector: {
              text: {},
            },
          },
          {
            name: "show_header",
            selector: {
              boolean: {},
            },
          },
        ],
        computeLabel: (schema) => {
          const labels = {
            config_entry: "Vehicle",
            view: "Card",
            layout: "Layout",
            period: "Period",
            title: "Custom title",
            show_header: "Show header",
          };
          return labels[schema.name];
        },
        computeHelper: (schema) => {
          if (schema.name === "config_entry") {
            return "Choose the Tessie Drive Stats vehicle. If only one vehicle exists, this can be left blank.";
          }
          if (schema.name === "period") {
            return "Used by Overview, Drive, Charging Economics, and Idle & Vampire.";
          }
          return undefined;
        },
      };
    }

    setConfig(config) {
      const view = config.view ?? "overview";
      const layout = config.layout ?? "auto";
      const period = config.period ?? "this_month";

      if (!VIEW_VALUES.has(view)) {
        throw new Error(`Unknown Tessie Drive Stats card view: ${view}`);
      }
      if (!LAYOUT_VALUES.has(layout)) {
        throw new Error(`Unknown Tessie Drive Stats card layout: ${layout}`);
      }
      if (!PERIOD_VALUES.has(period)) {
        throw new Error(`Unknown Tessie Drive Stats card period: ${period}`);
      }

      this._config = {
        ...config,
        view,
        layout,
        period,
        show_header: config.show_header !== false,
      };

      if (this._resolvedConfigEntry !== this._config.config_entry) {
        this._entityMap = new Map();
        this._resolvedConfigEntry = null;
        this._resolvingConfigEntry = null;
      }

      this._queueRender();
    }

    set hass(hass) {
      this._hass = hass;
      if (
        this._config?.config_entry &&
        this._resolvedConfigEntry !== this._config.config_entry &&
        this._resolvingConfigEntry !== this._config.config_entry
      ) {
        void this._resolveEntityRegistry(this._config.config_entry);
      }
      this._queueRender();
    }

    getCardSize() {
      const sizes = {
        overview: 5,
        drive: 6,
        efficiency: 6,
        charging: 6,
        charging_economics: 7,
        battery: 7,
        lifetime: 8,
        idle: 7,
      };
      return sizes[this._config?.view ?? "overview"] ?? 6;
    }

    getGridOptions() {
      const wide = this._config?.layout === "wide";
      return {
        columns: wide ? 12 : 6,
        min_columns: 3,
      };
    }

    async _resolveEntityRegistry(configEntryId) {
      if (!this._hass) return;
      this._resolvingConfigEntry = configEntryId;

      try {
        const entries = await this._hass.callWS({
          type: "config/entity_registry/list",
        });

        if (this._config?.config_entry !== configEntryId) return;

        const map = new Map();
        for (const entry of entries ?? []) {
          const entryConfigId = entry.config_entry_id;
          const belongs =
            entryConfigId === configEntryId ||
            (Array.isArray(entryConfigId) && entryConfigId.includes(configEntryId));
          if (!belongs || !entry.unique_id || !entry.entity_id) continue;

          for (const key of SORTED_KEYS) {
            if (entry.unique_id.endsWith(`_${key}`)) {
              map.set(key, entry.entity_id);
              break;
            }
          }
        }

        this._entityMap = map;
        this._resolvedConfigEntry = configEntryId;
      } catch (err) {
        console.warn("[Tessie Drive Stats Card] Unable to resolve entity registry", err);
        this._resolvedConfigEntry = configEntryId;
      } finally {
        if (this._resolvingConfigEntry === configEntryId) {
          this._resolvingConfigEntry = null;
        }
        this._queueRender();
      }
    }

    _queueRender() {
      if (this._renderQueued) return;
      this._renderQueued = true;
      requestAnimationFrame(() => {
        this._renderQueued = false;
        this._render();
      });
    }

    _prefixFromEntity(entityId) {
      if (!entityId || !entityId.includes(".")) return null;
      const objectId = entityId.slice(entityId.indexOf(".") + 1);

      for (const key of SORTED_KEYS) {
        const suffix = `_${key}`;
        if (objectId.endsWith(suffix)) {
          return objectId.slice(0, -key.length);
        }
      }
      return null;
    }

    _fallbackPrefix() {
      if (!this._hass) return null;

      const configured = this._prefixFromEntity(this._config?.entity);
      if (configured) return configured;

      const candidates = Object.keys(this._hass.states).filter(
        (entityId) =>
          entityId.startsWith("sensor.") && entityId.endsWith("_vehicle_status"),
      );

      if (candidates.length === 1) {
        return this._prefixFromEntity(candidates[0]);
      }

      return null;
    }

    _entityId(key) {
      const registryEntity = this._entityMap.get(key);
      if (registryEntity) return registryEntity;

      const prefix = this._fallbackPrefix();
      if (!prefix) return null;

      const domain = BINARY_KEYS.has(key) ? "binary_sensor" : "sensor";
      return `${domain}.${prefix}${key}`;
    }

    _obj(key) {
      const entityId = this._entityId(key);
      return entityId ? this._hass?.states?.[entityId] : undefined;
    }

    _raw(key, fallback = "—") {
      const obj = this._obj(key);
      const value = obj?.state;
      if (
        value === undefined ||
        value === null ||
        value === "" ||
        ["unknown", "unavailable", "none"].includes(String(value).toLowerCase())
      ) {
        return fallback;
      }
      return value;
    }

    _num(key) {
      const raw = this._raw(key, null);
      if (raw === null) return null;
      const value = Number(raw);
      return Number.isFinite(value) ? value : null;
    }

    _unit(key) {
      return this._obj(key)?.attributes?.unit_of_measurement ?? "";
    }

    _fmt(key, decimals = 1) {
      const value = this._num(key);
      if (value === null) return "—";
      return value.toLocaleString(this._hass?.locale?.language || undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });
    }

    _fmtWithUnit(key, decimals = 1) {
      const value = this._fmt(key, decimals);
      if (value === "—") return value;
      const unit = this._unit(key);
      return `${value}${unit ? ` <small>${escapeHtml(unit)}</small>` : ""}`;
    }

    _metric(icon, label, key, decimals = 1, pretty = false) {
      const value = pretty
        ? escapeHtml(titleCase(this._raw(key)))
        : this._fmtWithUnit(key, decimals);
      return `
        <div class="metric">
          <div class="metric-icon"><ha-icon icon="${icon}"></ha-icon></div>
          <div class="metric-copy">
            <span>${escapeHtml(label)}</span>
            <b>${value}</b>
          </div>
        </div>
      `;
    }

    _simple(label, key, decimals = 1, pretty = false) {
      const value = pretty
        ? escapeHtml(titleCase(this._raw(key)))
        : this._fmtWithUnit(key, decimals);
      return `
        <div class="simple">
          <span>${escapeHtml(label)}</span>
          <b>${value}</b>
        </div>
      `;
    }

    _periodLabel() {
      return PERIODS.find(([value]) => value === this._config.period)?.[1] ?? "This Month";
    }

    _viewTitle() {
      const defaultTitle =
        VIEWS.find(([value]) => value === this._config.view)?.[1] ?? "Tessie Drive Stats";
      return this._config.title || defaultTitle;
    }

    _header(icon, kicker, badge = "") {
      if (!this._config.show_header) return "";
      return `
        <div class="card-head">
          <div>
            <div class="kicker">${escapeHtml(kicker)}</div>
            <div class="card-title">
              <ha-icon icon="${icon}"></ha-icon>
              ${escapeHtml(this._viewTitle())}
            </div>
          </div>
          ${badge}
        </div>
      `;
    }

    _loadingOrSelectionMessage() {
      if (this._config?.config_entry && this._resolvingConfigEntry) {
        return "Loading Tessie Drive Stats entities…";
      }
      return "Select a Tessie Drive Stats vehicle in the card editor. If you use YAML, set config_entry or entity.";
    }

    _renderOverview() {
      const period = this._config.period;
      const battery = this._num("battery_level_current");
      const batteryWidth = battery === null ? 0 : Math.max(0, Math.min(100, battery));
      const status = titleCase(this._raw("vehicle_status"));
      const connection = titleCase(this._raw("connection_status"));
      const charging = titleCase(this._raw("charging_state_current"));

      return `
        ${this._header("mdi:car-electric", this._periodLabel())}
        <div class="vehicle-hero">
          <div class="vehicle-copy">
            <div class="vehicle-name">Tessie Drive Stats</div>
            <div class="vehicle-state">${escapeHtml(status)} · ${escapeHtml(connection)}</div>
          </div>
          <div class="hero-grid">
            ${this._simple("Battery", "battery_level_current", 0)}
            ${this._simple("Range", "battery_range_current", 0)}
            <div class="simple">
              <span>Charging</span>
              <b>${escapeHtml(charging)}</b>
            </div>
          </div>
        </div>
        <div class="battery-track"><i style="width:${batteryWidth}%"></i></div>
        <div class="metrics">
          ${this._metric("mdi:map-marker-distance", `${this._periodLabel()} Miles`, `miles_${period}`, 1)}
          ${this._metric("mdi:speedometer", "Driving Efficiency", `efficiency_${period}`, 0)}
          ${this._metric("mdi:cash", "Estimated Driving Cost", `estimated_driving_cost_${period}`, 2)}
          ${this._metric("mdi:road-variant", "Estimated Cost / Mile", `estimated_drive_cost_per_mile_${period}`, 4)}
          ${this._metric("mdi:battery-heart-variant", "Battery Health", "battery_health", 1)}
          ${this._metric("mdi:thermometer", "Outside Temperature", "outside_temperature_current", 1)}
        </div>
      `;
    }

    _renderDrive() {
      const period = this._config.period;
      return `
        ${this._header(
          "mdi:steering",
          "LAST DRIVE",
          `<div class="badge">${this._fmtWithUnit("last_drive_miles", 1)}</div>`,
        )}
        <div class="hero-grid hero-large">
          ${this._simple("Efficiency", "last_drive_efficiency", 0)}
          ${this._simple("Battery Used", "last_drive_battery_used", 1)}
        </div>
        <div class="metrics">
          ${this._metric("mdi:clock-outline", "Drive Time", "last_drive_time", 1)}
          ${this._metric("mdi:speedometer", "Average Speed", "last_drive_average_speed", 0)}
          ${this._metric("mdi:speedometer-medium", "Max Speed", "last_drive_max_speed", 0)}
          ${this._metric("mdi:thermometer", "Outside Temperature", "last_drive_outside_temperature", 1)}
          ${this._metric("mdi:home-thermometer-outline", "Cabin Temperature", "last_drive_inside_temperature", 1)}
          ${this._metric("mdi:steering", "AP / FSD Miles", "last_drive_autopilot_fsd_miles", 1)}
        </div>
        <div class="period-strip">
          <span>${escapeHtml(this._periodLabel())}</span>
          <b>${this._fmtWithUnit(`miles_${period}`, 1)}</b>
          <b>${this._fmtWithUnit(`drive_time_${period}`, 0)}</b>
          <b>${this._fmtWithUnit(`energy_${period}`, 2)}</b>
          <b>${this._fmtWithUnit(`efficiency_${period}`, 0)}</b>
        </div>
      `;
    }

    _comparison(label, deltaKey, baselineKey) {
      const delta = this._num(deltaKey);
      const className =
        delta === null ? "neutral" : delta > 5 ? "bad" : delta < -5 ? "good" : "neutral";
      const display =
        delta === null ? "—" : `${delta > 0 ? "+" : ""}${delta.toFixed(1)}%`;
      return `
        <div class="comparison ${className}">
          <div>
            <span>${escapeHtml(label)}</span>
            <b>${display}</b>
          </div>
          <small>${this._fmtWithUnit(baselineKey, 0)}</small>
        </div>
      `;
    }

    _renderEfficiency() {
      const alert = String(this._raw("last_drive_unusually_inefficient", "off")).toLowerCase() === "on";
      const badge = `<div class="badge ${alert ? "bad" : "good"}">${alert ? "HIGH USAGE" : "NORMAL"}</div>`;

      return `
        ${this._header("mdi:gauge", "DRIVE ENERGY FACTORS", badge)}
        <div class="hero-grid hero-large">
          ${this._simple("Last Drive Efficiency", "last_drive_efficiency", 0)}
          ${this._simple("Efficiency Percentile", "last_drive_efficiency_percentile", 0)}
        </div>
        <div class="comparison-grid">
          ${this._comparison("VS 30-DAY", "last_drive_efficiency_vs_30_day", "last_drive_efficiency_30_day_average")}
          ${this._comparison(
            "VS SIMILAR TEMPERATURE",
            "last_drive_efficiency_vs_similar_temperature",
            "last_drive_similar_temperature_efficiency",
          )}
          ${this._comparison(
            "VS SIMILAR SPEED",
            "last_drive_efficiency_vs_similar_speed",
            "last_drive_similar_speed_efficiency",
          )}
        </div>
        <div class="hero-grid">
          ${this._simple("Temperature Band", "last_drive_temperature_band", 0, true)}
          ${this._simple("Speed Band", "last_drive_speed_band", 0, true)}
        </div>
        <div class="context-row">
          <ha-icon icon="mdi:chart-line"></ha-icon>
          <div>
            <span>EFFICIENCY CONTEXT</span>
            <b>${escapeHtml(titleCase(this._raw("last_drive_efficiency_context")))}</b>
          </div>
        </div>
      `;
    }

    _renderCharging() {
      const chargingRaw = String(this._raw("charging_state_current", ""));
      const active = chargingRaw.toLowerCase() === "charging";
      const badge = `<div class="badge ${active ? "good" : ""}">${escapeHtml(titleCase(chargingRaw || "Unknown"))}</div>`;

      return `
        ${this._header("mdi:ev-station", "CURRENT STATUS", badge)}
        <div class="hero-grid hero-three">
          ${this._simple("Power", "charger_power_current", 1)}
          ${this._simple("Rate", "charge_rate_current", 1)}
          ${this._simple("Charge Limit", "charge_limit", 0)}
        </div>
        <div class="metrics">
          ${this._metric("mdi:timer-outline", "Time to Full", "time_to_full_charge", 1)}
          ${this._metric("mdi:cash", "Last Charge Cost", "last_charge_cost", 2)}
          ${this._metric("mdi:lightning-bolt", "Last Charge Energy", "last_charge_energy_added", 2)}
          ${this._metric("mdi:cash", "Last Supercharger Cost", "last_supercharger_cost", 2)}
          ${this._metric("mdi:ev-station", "Last Supercharger Energy", "last_supercharger_energy_added", 2)}
        </div>
        <div class="hero-grid">
          ${this._simple("Last Charge", "last_charge_location", 0, true)}
          ${this._simple("Last Supercharger", "last_supercharger_location", 0, true)}
        </div>
      `;
    }

    _renderChargingEconomics() {
      const period = this._config.period;
      const coverage = this._num(`charging_cost_coverage_${period}`);
      const coverageDisplay = coverage === null ? "—" : `${coverage.toFixed(1)}%`;

      return `
        ${this._header("mdi:cash-multiple", this._periodLabel())}
        <div class="economics-hero">
          <div class="economics-primary">
            <span>ESTIMATED COST / MILE</span>
            <b>${this._fmtWithUnit(`estimated_drive_cost_per_mile_${period}`, 4)}</b>
          </div>
          <div class="coverage">
            <span>COST COVERAGE</span>
            <b>${coverageDisplay}</b>
          </div>
        </div>
        <div class="metrics">
          ${this._metric("mdi:cash", "Estimated Driving Cost", `estimated_driving_cost_${period}`, 2)}
          ${this._metric("mdi:cash-sync", "Average Rate", `average_charging_cost_per_kwh_${period}`, 4)}
          ${this._metric("mdi:battery-charging-high", "Charging Efficiency", `charging_efficiency_${period}`, 1)}
          ${this._metric("mdi:transmission-tower-export", "Charging Loss", `charging_loss_${period}`, 1)}
          ${this._metric("mdi:cash-sync", "Last Charge Rate", "last_charge_cost_per_kwh", 4)}
          ${this._metric("mdi:ev-station", "Last Supercharger Rate", "last_supercharger_cost_per_kwh", 4)}
        </div>
        <div class="rate-compare">
          ${this._simple(
            "Non-Supercharger",
            "recorded_lifetime_non_supercharger_average_cost_per_kwh",
            4,
          )}
          ${this._simple(
            "Supercharger",
            "recorded_lifetime_supercharger_average_cost_per_kwh",
            4,
          )}
          <div class="simple premium">
            <span>PREMIUM</span>
            <b>${this._fmtWithUnit("recorded_lifetime_supercharger_cost_premium", 1)}</b>
          </div>
        </div>
      `;
    }

    _renderBattery() {
      const battery = this._num("battery_level_current");
      const health = this._num("battery_health");
      const batteryWidth = battery === null ? 0 : Math.max(0, Math.min(100, battery));
      const badge = `<div class="badge good">${health === null ? "—" : `${health.toFixed(1)}%`}</div>`;

      return `
        ${this._header("mdi:battery-heart-variant", "PACK HEALTH", badge)}
        <div class="hero-grid hero-large">
          ${this._simple("State of Charge", "battery_level_current", 0)}
          ${this._simple("Range", "battery_range_current", 0)}
        </div>
        <div class="battery-track"><i style="width:${batteryWidth}%"></i></div>
        <div class="metrics">
          ${this._metric("mdi:battery-alert-variant-outline", "Degradation", "battery_degradation", 1)}
          ${this._metric("mdi:battery", "Current Capacity", "battery_capacity", 2)}
          ${this._metric("mdi:battery-check", "Original Capacity", "battery_original_capacity", 2)}
          ${this._metric("mdi:map-marker-distance", "Max Range", "battery_max_range", 1)}
          ${this._metric("mdi:map-marker-star", "Ideal Max Range", "battery_max_ideal_range", 1)}
          ${this._metric("mdi:map-marker-outline", "Ideal Current Range", "ideal_battery_range_current", 1)}
          ${this._metric("mdi:thermometer-low", "Pack Temp Min", "battery_module_temp_min", 1)}
          ${this._metric("mdi:thermometer-high", "Pack Temp Max", "battery_module_temp_max", 1)}
          ${this._metric("mdi:thermometer-lines", "Pack Temp Spread", "battery_module_temp_spread", 1)}
          ${this._metric("mdi:chart-line", "Capacity Δ 30d", "battery_capacity_change_30_days", 2)}
          ${this._metric("mdi:chart-line", "Range Δ 30d", "battery_max_range_change_30_days", 1)}
        </div>
      `;
    }

    _renderLifetime() {
      return `
        ${this._header("mdi:history", "TESSIE RECORDED HISTORY")}
        <div class="hero-grid hero-large">
          ${this._simple("Recorded Miles", "recorded_lifetime_miles", 0)}
          ${this._simple("Efficiency", "recorded_lifetime_efficiency", 0)}
        </div>
        <div class="metrics">
          ${this._metric("mdi:counter", "Drives", "recorded_lifetime_drives", 0)}
          ${this._metric("mdi:clock-outline", "Drive Time", "recorded_lifetime_drive_time", 0)}
          ${this._metric("mdi:lightning-bolt", "Drive Energy", "recorded_lifetime_drive_energy", 1)}
          ${this._metric("mdi:steering", "AP / FSD Miles", "recorded_lifetime_ap_fsd_miles", 0)}
          ${this._metric("mdi:chart-donut", "AP / FSD Share", "recorded_lifetime_ap_fsd_share", 1)}
          ${this._metric("mdi:ev-station", "Charge Sessions", "recorded_lifetime_charge_sessions", 0)}
          ${this._metric("mdi:battery-charging", "Charge Energy", "recorded_lifetime_charge_energy_added", 1)}
          ${this._metric("mdi:cash", "Charge Cost", "recorded_lifetime_charge_cost", 2)}
          ${this._metric("mdi:ghost", "Idle Energy", "recorded_lifetime_idle_energy", 1)}
          ${this._metric("mdi:chart-timeline-variant", "Battery Measurements", "recorded_lifetime_battery_measurements", 0)}
          ${this._metric("mdi:battery-minus", "Capacity Change", "recorded_lifetime_capacity_change", 2)}
        </div>
        <div class="context-row">
          <ha-icon icon="mdi:calendar-start"></ha-icon>
          <div>
            <span>RECORDED SINCE</span>
            <b>${escapeHtml(this._raw("recorded_lifetime_data_since"))}</b>
          </div>
        </div>
      `;
    }

    _renderIdle() {
      const period = this._config.period;
      return `
        ${this._header("mdi:ghost", `ENERGY WHILE PARKED · ${this._periodLabel().toUpperCase()}`)}
        <div class="hero-grid hero-large">
          ${this._simple("Idle Energy", `idle_energy_${period}`, 2)}
          ${this._simple("Battery Used", `idle_battery_used_${period}`, 1)}
        </div>
        <div class="metrics">
          ${this._metric("mdi:counter", "Idle Sessions", `idle_sessions_${period}`, 0)}
          ${this._metric("mdi:clock-outline", "Idle Time", `idle_time_${period}`, 0)}
          ${this._metric("mdi:cctv", "Sentry Time", `idle_sentry_time_${period}`, 0)}
          ${this._metric("mdi:fan", "Climate Time", `idle_climate_time_${period}`, 0)}
          ${this._metric("mdi:clock-outline", "Last Idle Time", "last_idle_time", 1)}
          ${this._metric("mdi:lightning-bolt", "Last Idle Energy", "last_idle_energy", 2)}
          ${this._metric("mdi:battery-minus", "Last Idle Battery", "last_idle_battery_used", 1)}
          ${this._metric("mdi:cctv", "Last Sentry Share", "last_idle_sentry_share", 1)}
          ${this._metric("mdi:fan", "Last Climate Share", "last_idle_climate_share", 1)}
        </div>
        <div class="context-row">
          <ha-icon icon="mdi:map-marker"></ha-icon>
          <div>
            <span>LAST IDLE LOCATION</span>
            <b>${escapeHtml(this._raw("last_idle_location"))}</b>
          </div>
        </div>
      `;
    }

    _viewContent() {
      switch (this._config.view) {
        case "overview":
          return this._renderOverview();
        case "drive":
          return this._renderDrive();
        case "efficiency":
          return this._renderEfficiency();
        case "charging":
          return this._renderCharging();
        case "charging_economics":
          return this._renderChargingEconomics();
        case "battery":
          return this._renderBattery();
        case "lifetime":
          return this._renderLifetime();
        case "idle":
          return this._renderIdle();
        default:
          return "";
      }
    }

    _render() {
      if (!this.shadowRoot || !this._config || !this._hass) return;

      const hasRegistryMap = this._entityMap.size > 0;
      const hasFallback = Boolean(this._fallbackPrefix());
      const waitingForRegistry =
        Boolean(this._config.config_entry) &&
        this._resolvedConfigEntry !== this._config.config_entry;

      let content;
      if (!hasRegistryMap && !hasFallback) {
        content = waitingForRegistry
          ? `<div class="message">${escapeHtml(this._loadingOrSelectionMessage())}</div>`
          : `<div class="message">${escapeHtml(this._loadingOrSelectionMessage())}</div>`;
      } else {
        content = this._viewContent();
      }

      this.shadowRoot.innerHTML = `
        <ha-card>
          <div class="wrap layout-${escapeHtml(this._config.layout)}">
            ${content}
          </div>
        </ha-card>
        <style>
          :host {
            display: block;
            font-family: var(--ha-font-family-body, inherit);
          }

          ha-card {
            overflow: hidden;
            container-type: inline-size;
          }

          .wrap {
            box-sizing: border-box;
            padding: 16px;
            color: var(--primary-text-color);
          }

          .layout-compact {
            padding: 12px;
          }

          .layout-wide {
            padding: 20px;
          }

          .card-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding-bottom: 11px;
            margin-bottom: 12px;
            border-bottom: 1px solid var(--divider-color);
          }

          .kicker,
          .simple span,
          .metric-copy span,
          .comparison span,
          .context-row span,
          .vehicle-name,
          .economics-primary span,
          .coverage span,
          .period-strip > span {
            color: var(--secondary-text-color);
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
          }

          .card-title {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 3px;
            font-size: 1.08rem;
            font-weight: 700;
          }

          .card-title ha-icon {
            color: var(--primary-color);
            --mdc-icon-size: 19px;
          }

          .badge {
            max-width: 45%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding: 6px 9px;
            border: 1px solid var(--divider-color);
            border-radius: var(--ha-card-border-radius, 12px);
            color: var(--secondary-text-color);
            font-size: 0.7rem;
            font-weight: 700;
          }

          .good {
            color: var(--success-color, var(--primary-color));
          }

          .bad {
            color: var(--error-color, var(--primary-color));
          }

          .vehicle-hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
          }

          .vehicle-copy {
            min-width: 0;
          }

          .vehicle-name {
            color: var(--primary-color);
          }

          .vehicle-state {
            margin-top: 4px;
            color: var(--secondary-text-color);
            font-size: 0.8rem;
          }

          .hero-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
            margin-top: 8px;
          }

          .vehicle-hero .hero-grid {
            min-width: min(100%, 280px);
            margin-top: 0;
          }

          .hero-three {
            grid-template-columns: repeat(3, minmax(0, 1fr));
          }

          .hero-large .simple b {
            font-size: 1.45rem;
          }

          .simple,
          .metric,
          .comparison,
          .context-row,
          .period-strip,
          .economics-hero {
            border: 1px solid var(--divider-color);
            border-radius: var(--ha-card-border-radius, 12px);
            background: var(--secondary-background-color);
          }

          .simple {
            min-width: 0;
            padding: 10px 11px;
          }

          .simple b {
            display: block;
            margin-top: 3px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 0.9rem;
          }

          small {
            color: var(--secondary-text-color);
            font-size: 0.72em;
            font-weight: 500;
          }

          .battery-track {
            height: 5px;
            margin: 11px 0;
            overflow: hidden;
            border-radius: var(--ha-card-border-radius, 12px);
            background: var(--divider-color);
          }

          .battery-track i {
            display: block;
            height: 100%;
            background: var(--primary-color);
          }

          .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
            gap: 8px;
            margin-top: 8px;
          }

          .metric {
            display: flex;
            align-items: center;
            gap: 9px;
            min-width: 0;
            padding: 9px;
          }

          .metric-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            flex: 0 0 30px;
            border-radius: var(--ha-card-border-radius, 12px);
            background: var(--primary-background-color);
          }

          .metric-icon ha-icon {
            color: var(--primary-text-color);
            --mdc-icon-size: 16px;
          }

          .metric-copy {
            min-width: 0;
          }

          .metric-copy b {
            display: block;
            margin-top: 2px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 0.86rem;
          }

          .period-strip {
            display: grid;
            grid-template-columns: auto repeat(4, minmax(0, 1fr));
            align-items: center;
            gap: 8px;
            margin-top: 8px;
            padding: 9px 11px;
          }

          .period-strip b {
            overflow: hidden;
            text-align: right;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 0.74rem;
          }

          .comparison-grid {
            display: grid;
            gap: 8px;
            margin-top: 8px;
          }

          .comparison {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 10px 11px;
          }

          .comparison b {
            display: block;
            margin-top: 2px;
            font-size: 0.95rem;
          }

          .comparison small {
            text-align: right;
          }

          .comparison.good b {
            color: var(--success-color, var(--primary-color));
          }

          .comparison.bad b {
            color: var(--error-color, var(--primary-color));
          }

          .context-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 8px;
            padding: 10px 11px;
          }

          .context-row ha-icon {
            color: var(--primary-color);
            --mdc-icon-size: 18px;
          }

          .context-row b {
            display: block;
            margin-top: 2px;
            font-size: 0.82rem;
          }

          .economics-hero {
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 8px;
            margin-top: 8px;
            padding: 12px;
          }

          .economics-primary b,
          .coverage b {
            display: block;
            margin-top: 3px;
            font-size: 1.4rem;
          }

          .coverage b {
            color: var(--success-color, var(--primary-color));
          }

          .rate-compare {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin-top: 8px;
          }

          .premium b {
            color: var(--warning-color, var(--primary-color));
          }

          .message {
            padding: 16px;
            color: var(--secondary-text-color);
            text-align: center;
          }

          .layout-compact .metrics {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }

          .layout-compact .metric {
            padding: 8px;
          }

          .layout-compact .metric-icon {
            width: 27px;
            height: 27px;
            flex-basis: 27px;
          }

          .layout-wide .metrics {
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          }

          @container (max-width: 520px) {
            .wrap,
            .layout-wide {
              padding: 12px;
            }

            .vehicle-hero {
              align-items: stretch;
              flex-direction: column;
            }

            .vehicle-hero .hero-grid {
              min-width: 0;
            }

            .hero-three {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .hero-three .simple:last-child {
              grid-column: 1 / -1;
            }

            .period-strip {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .period-strip > span {
              grid-column: 1 / -1;
            }

            .period-strip b {
              text-align: left;
            }

            .economics-hero,
            .rate-compare {
              grid-template-columns: 1fr;
            }
          }

          @container (max-width: 360px) {
            .hero-grid,
            .metrics,
            .layout-compact .metrics {
              grid-template-columns: 1fr;
            }
          }
        </style>
      `;
    }
  }

  function suggestedPrefixEntity(entityId) {
    if (!entityId || !entityId.includes(".")) return null;
    const objectId = entityId.slice(entityId.indexOf(".") + 1);
    for (const key of SORTED_KEYS) {
      const suffix = `_${key}`;
      if (objectId.endsWith(suffix)) {
        return entityId;
      }
    }
    return null;
  }

  function suggestionForEntity(hass, entityId) {
    const anchor = suggestedPrefixEntity(entityId);
    if (!anchor || !hass?.states?.[entityId]) return null;

    const objectId = entityId.slice(entityId.indexOf(".") + 1);
    const matchedKey = SORTED_KEYS.find((key) => objectId.endsWith(`_${key}`));
    const base = {
      type: CARD_TYPE,
      entity: anchor,
      layout: "auto",
      period: "this_month",
      show_header: true,
    };

    const suggestions = [
      {
        label: "Overview",
        config: { ...base, view: "overview" },
      },
    ];

    if (matchedKey?.includes("charging") || matchedKey?.includes("charge")) {
      suggestions.push(
        { label: "Charging", config: { ...base, view: "charging" } },
        {
          label: "Charging Economics",
          config: { ...base, view: "charging_economics" },
        },
      );
    } else if (matchedKey?.includes("idle")) {
      suggestions.push({
        label: "Idle & Vampire",
        config: { ...base, view: "idle" },
      });
    } else if (matchedKey?.startsWith("recorded_lifetime")) {
      suggestions.push({
        label: "Lifetime",
        config: { ...base, view: "lifetime" },
      });
    } else if (matchedKey?.includes("battery")) {
      suggestions.push({
        label: "Battery",
        config: { ...base, view: "battery" },
      });
    } else if (
      matchedKey?.startsWith("last_drive") ||
      matchedKey?.includes("efficiency")
    ) {
      suggestions.push(
        { label: "Drive", config: { ...base, view: "drive" } },
        { label: "Efficiency", config: { ...base, view: "efficiency" } },
      );
    }

    return suggestions;
  }

  if (!customElements.get(CARD_TAG)) {
    customElements.define(CARD_TAG, TessieDriveStatsCard);
  }

  window.customCards = window.customCards || [];
  if (!window.customCards.some((card) => card.type === CARD_TAG)) {
    window.customCards.push({
      type: CARD_TAG,
      name: "Tessie Drive Stats",
      description:
        "Theme-aware Tesla analytics cards for Tessie Drive Stats.",
      preview: true,
      documentationURL:
        "https://github.com/LiquidFXX/tessie-drive-stats",
      getEntitySuggestion: suggestionForEntity,
    });
  }
})();
