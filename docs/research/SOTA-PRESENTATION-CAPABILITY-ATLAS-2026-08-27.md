# SOTA Presentation Capability Atlas for Shannon Insight

Evidence cutoff 2026-08-27; baseline `1546155603aab9c24cbb9702616322b5683a8059`. Research candidate only.

## Architecture
`QuestionIntent -> TypedAnalyticalResult -> deterministic constraints -> PresentationPlan -> (visual grammar | typed specialist) -> interaction/artifact -> accessibility/evidence/policy/resource gates -> renderer/export/embed`. Vendor names are evidence only.

Coverage: 50 products; 82 sources; 142 patterns; 68 intents; 17 specialist families; 50 target seams.

## 50 SOTA products and observed presentation surface

- Celonis / Process Intelligence / Studio: process_map, variant_explorer, throughput_explorer, process_animation, process_filters, root_cause_handoff
- UiPath / Process Mining: process_graph, variant_control, kpi_bar, cross_analysis_table, process_heatmap
- SAP / Signavio Process Intelligence: process_discovery, process_conformance, variant_explorer, process_funnel, activity_list, live_insights
- Apromore / Apromore: process_map, variant_inspector, frequency_duration_cost_overlays, bpmn_view, root_cause_analysis, saved_process_view
- Microsoft / Power BI: interactive_report, dashboard, paginated_report, matrix, decomposition_tree, key_influencers, map, bookmark, drillthrough
- Salesforce / Tableau: worksheet, dashboard, story, show_me_recommendation, small_multiples, maps, highlight_table, box_plot
- Qlik / Qlik Sense / Qlik Cloud Analytics: intent_analysis_types, associative_exploration, kpi, geospatial_breakdown, pareto, control_chart, forecast, anomaly
- Google Cloud / Looker: explore, dashboard, single_value, boxplot, waterfall, funnel, timeline, map, custom_visualization
- ThoughtSpot / ThoughtSpot: liveboard, natural_language_analysis, automatic_chart_selection, visual_explorer, watchlist, custom_charts
- Sigma Computing / Sigma: workbook, table, pivot, dashboard_layout, chart, input_table, app_ui, report_export
- Oracle / Oracle Analytics: auto_visualization, network_graph, maps, grid, narrative, gauge, dashboard_controls
- SAP / SAP Analytics Cloud: story, analytic_application, variance_chart, waterfall, time_series, geo_layers, planning_table, in_cell_chart
- IBM / Cognos Analytics: dashboard, story, auto_visualization, map, table, chart, plot
- Spotfire / Spotfire: marking, linked_visualizations, data_functions, statistical_tools, maps, custom_mods
- Strategy / Strategy One: grid, heatmap, dual_axis, network, histogram, boxplot, waterfall, sankey, geospatial, kpi
- Sisense / Sisense: widget, dashboard, pivot, scatter, kpi, map, recommended_widget
- Domo / Domo: card, dashboard, chart_compatibility_picker, maps, sparklines, running_total, funnel
- Metabase / Metabase: question, dashboard, auto_chart, pivot, sankey, waterfall, funnel, map, progress
- Apache Software Foundation / Apache Superset: explore, dashboard, 40_plus_visualizations, geospatial, plugin_visualization, sql_lab
- Palantir / Foundry Quiver / Contour / Workshop: object_chart, time_series_analysis, dashboard, dependency_graph, operational_app_embedding, parameterized_analysis
- Dataiku / Dataiku DSS: dataset_chart, visual_analysis_chart, dashboard_insight, model_report, map, scatter, animated_chart, subcharts
- ThoughtSpot / Mode Analytics: sql_report, quick_chart, python_r_visual, custom_javascript_visual, report_filter
- Rill Data / Rill: explore_dashboard, dimension_leaderboard, time_dimension_detail, pivot, multiple_measures
- Grafana Labs / Grafana: time_series, state_timeline, status_history, logs, traces, flame_graph, node_graph, geomap, candlestick, alert_list
- Datadog / Datadog: timeseries, distribution, heatmap, top_list, flame_graph, topology_map, hostmap, slo, funnel, retention, sankey
- Dynatrace / Dynatrace: band_chart, honeycomb, choropleth, connection_map, record_list, davis_view, dashboard_document
- New Relic / New Relic: area, bar, billboard, gauge, heatmap, histogram, line, table, auto_chart
- Elastic / Kibana Lens: lens, xy_layer, partition_chart, metric, table, maps, vega_custom, annotations, reference_lines
- Cisco / Splunk Dashboard Studio: event_viewer, time_series, bubble, choropleth, svg_choropleth, sankey, timeline, custom_visualization
- Honeycomb / Honeycomb: heatmap, bubbleup, correlation_views, trace_view, events_view, query_assistant
- Amplitude / Amplitude Analytics: event_segmentation, funnel, retention, journeys, engagement_matrix, personas, impact_analysis, stickiness, lifecycle, ltv
- Google / Google Analytics 4 Explorations: funnel_exploration, path_tree, cohort_exploration, segment_overlap, free_form
- Anaplan / Anaplan UX: worksheet, board, report, editable_grid, kpi_card, field_input, scenario
- Workday / Adaptive Planning: dashboard, sheet, matrix_report, report_book, scenario, prediction_vs_plan
- Oracle / Primavera P6 Professional: gantt, resource_usage_histogram, resource_usage_spreadsheet, time_phased_curve, s_curve
- Bloomberg / Bloomberg Terminal / BQuant: market_monitor, instrument_chart, candlestick, yield_curve, scenario_analysis, portfolio_report, heatmap, map, notebook_app
- Esri / ArcGIS Dashboards: map, serial_chart, pie, indicator, gauge, list, table, details, selectors
- CARTO / CARTO Builder: map, formula_widget, category_widget, histogram_widget, range_widget, time_series_widget, table_widget
- Mapbox / Mapbox Studio / GL: choropleth, data_driven_circle, data_driven_line, 3d_extrusion, heatmap, symbol_map
- Neo4j / Neo4j Bloom: graph_scene, perspective, relationship_filter, business_view, custom_search_phrase
- Seeq / Seeq Workbench: trend_view, xy_plot, tables_charts, treemap, summary_report, capsule_intervals
- AVEVA / PI Vision: realtime_display, trend, gauge, color_coded_symbol, asset_collection, ad_hoc_analysis, visual_alarm
- Canva / Flourish: 50_plus_templates, story, scrollytelling, animation, responsive_chart, survey_view, hierarchy_graph
- Datawrapper / Datawrapper: accessible_chart, choropleth, symbol_map, locator_map, table_heatmap, small_chart_in_table, annotation
- Observable / Observable Plot / Framework: mark_grammar, layered_marks, transforms, facets, geo, raster, vector, tree, regression
- Plotly / Plotly / Dash: 3d_surface, volume, isosurface, streamtube, ternary, polar, parallel_coordinates, sankey, sunburst, scientific_contour
- Hex / Hex: chart_cell, notebook, app_builder, input_control, filtered_dataframe_output
- Snowflake / Streamlit: native_chart, vega_lite, plotly, pydeck, graphviz, mermaid, interactive_input
- Project Jupyter / Jupyter / ipywidgets: notebook, mime_output, interactive_widget, rich_display, code_narrative
- Autodesk / Tandem: 3d_twin_view, saved_view, asset_inventory, color_coding, clustering, section_plane

## 142 normalized patterns

- comparison_ranking: bar, grouped_bar, stacked_bar, normalized_stacked_bar, dot_plot, lollipop, range_plot, slopegraph, pareto, small_multiples
- composition_hierarchy: donut, treemap, sunburst, icicle, waffle, packed_circles, tree
- distribution_uncertainty: histogram, density, ecdf, boxplot, violin, strip, beeswarm, ridgeline, error_bar, interval_band, fan_chart, ensemble_spaghetti, quantile_plot
- finance_project: candlestick, yield_curve, drawdown, budget_variance, gantt, resource_histogram, s_curve, milestone_timeline
- flow_sequence: sankey, alluvial, funnel, journey_path, event_sequence, chord
- geospatial: choropleth, proportional_symbol_map, dot_density_map, spatial_heatmap, hex_grid_map, flow_map, route_trajectory, isoline, raster_map, extruded_3d_map
- graph_knowledge: node_link, force_graph, hierarchical_network, adjacency_matrix, ego_graph, dependency_wheel
- industrial_scientific: signal_trend, xy_signal, capsule_lane, spectrogram, waveform, spectrum, contour_field, vector_field, streamlines, surface_3d, mesh_3d, volume_render, isosurface, point_cloud
- narrative_artifact: annotated_visual, story_sequence, scrollytelling, dashboard, scorecard, wallboard, paginated_report, notebook_output, saved_3d_view
- observability: state_timeline, status_history, logs_view, trace_waterfall, flame_graph, service_topology, hostmap, slo_panel, bubbleup_contrast
- process_intelligence: process_map, process_variant_explorer, conformance_overlay, throughput_explorer, process_animation, activity_frequency, case_explorer
- product_behavior: retention_cohort, lifecycle_matrix, segment_overlap, path_sunburst, impact_analysis, stickiness_curve
- relationship_multivariate: scatter, bubble, hexbin, density_contour, regression_plot, correlation_matrix, scatterplot_matrix, parallel_coordinates, heatmap, ternary, polar, radar
- summary_status: single_value, kpi_with_delta, sparkline_kpi, bullet_chart, progress_bar, gauge, traffic_light
- tabular_grid: table, matrix, pivot, conditional_table, table_sparklines, planning_grid
- time_change: line, multi_line, step_line, area, stacked_area, streamgraph, horizon, calendar_heatmap, waterfall, index_chart, control_chart, run_chart

## 68 question-intent routes

- headline_status -> single_value/kpi_with_delta/sparkline_kpi [generic]
- progress_to_target -> bullet_chart/progress_bar/kpi_with_delta [generic]
- compare_categories -> bar/dot_plot/grouped_bar [generic]
- rank_entities -> bar/lollipop/pareto/table [generic]
- compare_two_states -> slopegraph/range_plot/grouped_bar [generic]
- trend_over_time -> line/sparkline_kpi/run_chart [generic]
- compare_time_series -> multi_line/small_multiples/index_chart/horizon [generic]
- composition_now -> bar/normalized_stacked_bar/treemap/donut [generic]
- composition_over_time -> stacked_area/normalized_stacked_bar/small_multiples [generic]
- hierarchy_size -> treemap/sunburst/icicle [generic]
- contribution_to_change -> waterfall/pareto/bar [generic]
- variance_to_plan -> budget_variance/waterfall/table [planning]
- distribution -> histogram/ecdf/boxplot/density [generic]
- compare_distributions -> boxplot/violin/ridgeline/ecdf [generic]
- outliers -> boxplot/scatter/strip/table [generic]
- relationship -> scatter/hexbin/regression_plot [generic]
- multivariate_relationship -> scatterplot_matrix/parallel_coordinates/correlation_matrix [generic]
- uncertainty_estimate -> error_bar/interval_band/quantile_plot [generic]
- forecast -> line/fan_chart/interval_band [generic]
- scenario_compare -> ensemble_spaghetti/fan_chart/small_multiples/table [planning]
- what_if -> planning_grid/line/waterfall/table [planning]
- optimization_tradeoff -> scatter/parallel_coordinates/table/small_multiples [decision_support]
- known_funnel -> funnel/bar/table [product_journey]
- unknown_paths -> journey_path/path_sunburst/sankey [product_journey]
- retention -> retention_cohort/heatmap/table [product_journey]
- stickiness -> stickiness_curve/histogram/bar [product_journey]
- segment_overlap -> segment_overlap/bar/table [product_journey]
- process_discovery -> process_map/case_explorer [process_intelligence]
- process_variants -> process_variant_explorer/bar/case_explorer [process_intelligence]
- process_conformance -> conformance_overlay/process_map/table [process_intelligence]
- process_bottleneck -> throughput_explorer/process_map/boxplot/pareto [process_intelligence]
- throughput_duration -> throughput_explorer/histogram/boxplot/pareto [process_intelligence]
- root_cause_contrast -> bubbleup_contrast/bar/table [observability_investigation]
- anomaly_over_time -> line/control_chart/heatmap [generic]
- process_control -> control_chart/run_chart [industrial_signal]
- live_monitoring -> wallboard/kpi_with_delta/line/state_timeline [observability_investigation]
- state_changes -> state_timeline/status_history [observability_investigation]
- service_topology -> service_topology/node_link/table [observability_investigation]
- latency_trace -> trace_waterfall/table [observability_investigation]
- code_profile -> flame_graph/table [observability_investigation]
- log_inspection -> logs_view/table [observability_investigation]
- slo_health -> slo_panel/line/kpi_with_delta [observability_investigation]
- geographic_distribution -> choropleth/hex_grid_map [geospatial]
- location_magnitude -> proportional_symbol_map/spatial_heatmap/hex_grid_map [geospatial]
- spatial_flow -> flow_map/route_trajectory [geospatial]
- spatial_field -> raster_map/isoline/spatial_heatmap [geospatial]
- network_structure -> node_link/force_graph/adjacency_matrix [graph_knowledge]
- network_dependency -> hierarchical_network/dependency_wheel/adjacency_matrix [graph_knowledge]
- ego_context -> ego_graph/node_link [graph_knowledge]
- signal_trend -> signal_trend/line [industrial_signal]
- signal_relationship -> xy_signal/scatter [industrial_signal]
- condition_intervals -> capsule_lane/state_timeline/signal_trend [industrial_signal]
- frequency_content -> spectrum/spectrogram/waveform [industrial_signal]
- project_schedule -> gantt/milestone_timeline/table [project_controls]
- resource_capacity -> resource_histogram/gantt/table [project_controls]
- cumulative_progress -> s_curve/multi_line [project_controls]
- market_price_action -> candlestick/line [finance_market]
- yield_term_structure -> yield_curve/line [finance_market]
- portfolio_drawdown -> drawdown/line [finance_market]
- scientific_scalar_field -> contour_field/surface_3d/volume_render/isosurface [scientific_field]
- scientific_vector_field -> vector_field/streamlines [scientific_field]
- 3d_structure -> mesh_3d/point_cloud/saved_3d_view [digital_twin]
- record_inspection -> table/case_explorer [generic]
- slice_and_dice -> pivot/matrix/bar/heatmap [generic]
- narrative_explanation -> story_sequence/annotated_visual/scrollytelling/small_multiples [storytelling]
- formal_publication -> paginated_report/table/annotated_visual [formal_reporting]
- evidence_provenance -> table/node_link/annotated_visual [generic]
- natural_language_question -> table [generic]

## 17 typed specialist families

- process_intelligence: Process intelligence
- product_journey: Product journey and behavioral analytics
- observability_investigation: Observability investigation
- planning: Planning and writeback
- finance_market: Market and portfolio analytics
- project_controls: Project controls
- geospatial: Geospatial analytical experience
- graph_knowledge: Graph and knowledge exploration
- industrial_signal: Industrial signal and condition analysis
- scientific_field: Scientific field visualization
- digital_twin: 3D / digital-twin inspection
- storytelling: Narrative and explanatory publishing
- formal_reporting: Formal and paginated reporting
- computational_document: Computational document and data app
- embedded_analytics: Embedded analytics
- self_service_visual_discovery: Self-service visual discovery
- decision_support: Decision support and analytical application

## SOTA laws

- Question intent and exact typed result precede chart choice.
- Ordinary statistical charts compile from a declarative grammar; named charts are recipes.
- Process, journey/cohort, observability, planning/writeback, finance, project, geo, graph, signal, scientific/3D, digital-twin, narrative/reporting, computational-document, embedded, self-service discovery, and decision-support semantics stay typed.
- LLMs may parse/propose; deterministic hard constraints admit/reject/rank.
- Dashboard != alert != notification != acknowledgment; exploration != formal reporting.
- Selection/filter/drill/bookmark != source entitlement or business effect; action/writeback emits a typed intent to separate authority.
- Uncertainty, missingness, accessibility task equivalence, provenance, policy and resource budgets survive every target or compilation refuses.
- Pixel similarity != semantic equivalence.
- Provider names never enter semantic dispatch.
- Completeness is capability saturation across unrelated products/verticals, not vendor count.

## 50 target seams

presentation_intent, result_presentation_binding, presentation_ir, statistical_visual_grammar, visual_recipe_catalog, visual_fitness_constraints, presentation_planner, composition_layout, responsive_layout, interaction_state, selection_algebra, drill_navigation, view_state_bookmark, table_grid_model, dashboard_runtime, story_narrative, report_definition, report_run, pagination_layout, publication_lifecycle, report_snapshot, export_plan, export_encoder, export_delivery, embedded_bridge, embed_entitlement_projection, accessibility_semantics, accessible_task_equivalent, localization_format, uncertainty_encoding, missingness_encoding, provenance_disclosure, annotation_collaboration, specialized_experience_registry, renderer_adapter, semantic_equivalence_oracle, visual_regression_oracle, presentation_resource_budget, presentation_usage_evidence, process_view_profile, journey_view_profile, observability_view_profile, geospatial_view_profile, graph_view_profile, signal_view_profile, scientific_scene_profile, planning_interaction_profile, finance_market_view_profile, project_control_view_profile, digital_twin_scene_profile

## Adoption sequence

- P0 - Evidence and capability atlas: Freeze normalized vocabulary; preserve vendor evidence separately; establish saturation and non-collapse laws.
- P1 - Intent, result binding and Presentation IR: Compile explicit question intent and exact analytical-result metadata into portable Presentation IR.
- P2 - Visual grammar, recipes and recommendation planner: Implement declarative marks/channels/scales plus named recipes; hard constraints reject invalid forms; soft constraints rank admissible candidates.
- P3 - Interaction and artifact composition: Unify linked selection/filter/drill/bookmark semantics and compose views into worksheets/dashboards/stories without effect authority.
- P4 - Typed specialized experiences: Bind specialized result predicates to typed profiles for process, journey, observability, geo, graph, signal, scientific, planning, finance, project and 3D/twin experiences.
- P5 - Accessibility, uncertainty, provenance and assurance: Make accessibility, missingness, uncertainty, provenance, resource limits and equivalence mandatory compilation obligations.
- P6 - Reporting, publication, export and embedding: Complete durable report lifecycle, snapshots, export carriers, delivery receipts and embedded host/guest contracts.
- P7 - Renderer/provider qualification and operational evidence: Qualify renderer/provider occurrences against exact conformance corpora, device/export targets, resource budgets and semantic-equivalence tests.

## Saturation

The 50-product, 12-archetype corpus plus a redundancy probe is sufficient to define a target horizontal suite candidate. It is not a claim that every vendor feature, proprietary chart, future product, or vertical presentation has been enumerated.

Continue sampling unrelated products and verticals until a redundancy probe adds no new root question intent, artifact lifecycle, interaction semantic, or specialized experience family.

## Evidence anchors

Current official/primary research covers Celonis, UiPath, SAP Signavio, Apromore; Power BI, Tableau, Qlik, Looker, ThoughtSpot, Sigma, Oracle Analytics, SAP Analytics Cloud, Cognos, Spotfire, Strategy, Sisense, Domo, Metabase, Superset; Palantir, Dataiku, Mode, Rill; Grafana, Datadog, Dynatrace, New Relic, Elastic, Splunk, Honeycomb; Amplitude, GA4; Anaplan, Workday, Primavera, Bloomberg; ArcGIS, CARTO, Mapbox, Neo4j, Seeq, AVEVA; Flourish, Datawrapper, Observable, Plotly, Hex, Streamlit, Jupyter, Autodesk Tandem; plus Munzner, Draco, Voyager, GraphScape, Olli, Vega-Lite and WCAG 2.2.

## Integration posture

Upstream research input only. Canonical generated adjudication remains `research/product_ontology/inventory_challenges/presentation_experience_gap_audit/`; promotion, qualification, vertical acceptance and ratification remain explicit later gates.
