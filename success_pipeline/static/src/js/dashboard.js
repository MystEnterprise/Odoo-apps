/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, onWillStart, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class SuccessPipelineDashboard extends Component {
    static template = xml`<div class="o_action"/>`;

    setup() {
        const orm = useService("orm");
        const action = useService("action");

        onWillStart(async () => {
            const ids = await orm.create("success.pipeline.stats", [{}]);
            action.doAction(
                {
                    type: "ir.actions.act_window",
                    res_model: "success.pipeline.stats",
                    res_id: ids[0],
                    views: [[false, "form"]],
                    target: "current",
                    context: { form_view_initial_mode: "readonly" },
                },
                { stackPosition: "replaceCurrentAction" }
            );
        });
    }
}

registry.category("actions").add("success_pipeline.dashboard", SuccessPipelineDashboard);
