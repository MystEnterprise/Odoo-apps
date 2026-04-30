from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import calendar as cal

STAGE_SELECTION = [
    ('lead_in', 'Lead In'),
    ('delivery_lead_confirmed', 'Delivery Lead Confirmed'),
    ('cso_confirmed', 'Source Lead Confirmed'),
    ('sourcing', 'Sourcing'),
    ('md_approval', '3P Approval'),
    ('closed_won', 'Closed Won'),
    ('closed_lost', 'Closed Lost'),
]

STATUS_SEL = [
    ('on_track', 'On Track'),
    ('near_miss', 'Near Miss'),
    ('off_track', 'Off Track'),
]

FILTER_PERIOD = [
    ('all', 'All Time'),
    ('this_month', 'This Month'),
    ('this_quarter', 'This Quarter'),
    ('this_year', 'This Year'),
]


class SuccessLead(models.Model):
    _name = 'success.lead'
    _description = 'Success Pipeline Lead'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_created desc, id desc'

    name = fields.Char(string='Deal Name', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    what_they_need = fields.Text(string='What They Need', tracking=True)
    qty = fields.Float(string='Quantity', digits=(16, 2), tracking=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id, required=True,
    )
    budget = fields.Monetary(string='Budget', currency_field='currency_id', tracking=True)
    timeline = fields.Date(string='Required By', tracking=True)
    product_type = fields.Selection(
        [('standard', 'Standard'), ('custom', 'Custom')],
        string='Product Type', default='standard', tracking=True,
    )
    cso_deadline = fields.Date(string='Delivery Lead Deadline', tracking=True)
    deal_value = fields.Monetary(string='Deal Value', currency_field='currency_id', tracking=True)
    outcome_notes = fields.Text(string='Outcome Notes', tracking=True)
    stage = fields.Selection(
        STAGE_SELECTION, string='Stage', default='lead_in',
        tracking=True, group_expand='_group_expand_stages', index=True,
    )
    user_id = fields.Many2one(
        'res.users', string='Growth Lead',
        default=lambda self: self.env.user, tracking=True,
    )
    cso_id = fields.Many2one('res.users', string='Delivery Lead', tracking=True)
    date_created = fields.Date(
        string='Date Created', default=fields.Date.today, readonly=True, copy=False,
    )
    date_closed = fields.Date(string='Date Closed', tracking=True)
    color = fields.Integer(string='Kanban Color')
    active = fields.Boolean(default=True)
    record_type = fields.Selection([('inquiry','Leads'),('innovation','Game-Changer')], string='Type', default='inquiry', required=True, tracking=True)

    @api.constrains('partner_id', 'record_type')
    def _check_partner_required_for_leads(self):
        for rec in self:
            if rec.record_type == 'inquiry' and not rec.partner_id:
                raise ValidationError('Customer is required for Lead records.')
    innovation_stage = fields.Selection([
        ('ideation','Ideation'),('feasibility','Feasibility'),('sourcing','Sourcing'),
        ('prototype','Prototype / MVP'),('scale','Scale'),('launch','Launch'),
        ('validation','Market Validation'),('established','Established'),('killed','Killed'),
    ], string='Innovation Stage', tracking=True, group_expand='_group_expand_innovation_stages')
    pain_point_severity = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], string='Pain Point Severity', tracking=True)
    unique_value_prop = fields.Char(string='Unique Value Proposition', tracking=True)
    inspiration_source = fields.Char(string='Inspiration Source', tracking=True)
    innovation_budget = fields.Monetary(string='Innovation Budget', currency_field='currency_id', tracking=True)
    target_customer_desc = fields.Char(string='Target Customer', tracking=True)
    problem_statement = fields.Text(string='Problem Statement', tracking=True)
    market_size_estimate = fields.Char(string='Market Size Estimate', tracking=True)
    competitor_analysis = fields.Text(string='Competitor Analysis', tracking=True)
    technical_feasibility = fields.Selection([('yes','Yes'),('partial','Partial'),('no','No')], string='Technical Feasibility', tracking=True)
    dev_cost_estimate = fields.Monetary(string='Dev Cost Estimate', currency_field='currency_id', tracking=True)
    go_no_go = fields.Selection([('yes','Go'),('no','No-Go')], string='Go / No-Go Decision', tracking=True)
    go_no_go_date = fields.Date(string='Decision Date', tracking=True)
    ip_patent_check = fields.Boolean(string='IP / Patent Checked', tracking=True)
    ip_notes = fields.Text(string='IP Notes', tracking=True)
    prototype_cost = fields.Monetary(string='Prototype Cost', currency_field='currency_id', tracking=True)
    testing_method = fields.Char(string='Testing Method', tracking=True)
    feedback_summary = fields.Text(string='Feedback Summary', tracking=True)
    iteration_notes = fields.Text(string='Iteration Notes', tracking=True)
    mvp_deadline = fields.Date(string='MVP Deadline', tracking=True)
    production_volume_target = fields.Float(string='Production Volume Target', tracking=True)
    unit_economics = fields.Char(string='Unit Economics', tracking=True)
    breakeven_units = fields.Float(string='Break-Even Units', tracking=True)
    supplier_confirmed_innovation = fields.Boolean(string='Supplier Confirmed', tracking=True)
    marketing_channels = fields.Char(string='Marketing Channels', tracking=True)
    launch_date = fields.Date(string='Launch Date', tracking=True)
    launch_market = fields.Selection([('local','Local Market'),('au','Australia'),('pacific','Pacific'),('global','Global')], string='Launch Market', tracking=True)
    launch_marketing_channel = fields.Char(string='Launch Marketing Channel', tracking=True)
    launch_budget = fields.Monetary(string='Launch Budget', currency_field='currency_id', tracking=True)
    units_sold = fields.Float(string='Units Sold', tracking=True)
    customer_feedback_score = fields.Float(string='Customer Feedback Score', digits=(5,2), tracking=True)
    return_rate = fields.Float(string='Return Rate %', digits=(5,2), tracking=True)
    nps_score = fields.Float(string='NPS Score', digits=(5,1), tracking=True)
    monthly_revenue = fields.Monetary(string='Monthly Revenue', currency_field='currency_id', tracking=True)
    reorder_frequency = fields.Char(string='Reorder Frequency', tracking=True)
    product_rating = fields.Float(string='Product Rating', digits=(3,1), tracking=True)
    expansion_markets = fields.Char(string='Expansion Markets', tracking=True)
    create_product = fields.Boolean(string='Add to Product Line', default=False, tracking=True)
    product_id = fields.Many2one('product.template', string='Linked Product', tracking=True)
    new_product_name = fields.Char(string='New Product Name', tracking=True)
    new_product_description = fields.Text(string='Product Description', tracking=True)
    ideation_notes = fields.Text(string='Ideation Notes', tracking=True)
    feasibility_notes = fields.Text(string='Feasibility Notes', tracking=True)
    sourcing_notes_inno = fields.Text(string='Innovation Sourcing Notes', tracking=True)
    prototype_notes = fields.Text(string='Prototype Notes', tracking=True)
    scale_notes = fields.Text(string='Scale Notes', tracking=True)
    launch_notes = fields.Text(string='Launch Notes', tracking=True)
    validation_notes = fields.Text(string='Validation Notes', tracking=True)
    established_notes = fields.Text(string='Established Notes', tracking=True)
    whatsapp_log = fields.Text(string='WhatsApp / WeChat Log', tracking=True)
    whatsapp_log_ideation = fields.Text(string='WhatsApp Log — Ideation', tracking=True)
    whatsapp_log_feasibility = fields.Text(string='WhatsApp Log — Feasibility', tracking=True)
    whatsapp_log_sourcing = fields.Text(string='WhatsApp Log — Sourcing', tracking=True)
    whatsapp_log_prototype = fields.Text(string='WhatsApp Log — Prototype / MVP', tracking=True)
    whatsapp_log_scale = fields.Text(string='WhatsApp Log — Scale', tracking=True)
    whatsapp_log_launch = fields.Text(string='WhatsApp Log — Launch', tracking=True)
    whatsapp_log_validation = fields.Text(string='WhatsApp Log — Market Validation', tracking=True)
    whatsapp_log_established = fields.Text(string='WhatsApp Log — Established', tracking=True)
    supplier_rating = fields.Selection([('1','1 - Poor'),('2','2 - Below Average'),('3','3 - Average'),('4','4 - Good'),('5','5 - Excellent')], string='Supplier Rating', tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company, required=True,
    )
    stage_date = fields.Date(string='Stage Since', readonly=True, copy=False)
    date_cso_confirmed = fields.Date(string='Source Lead Confirmed Date', readonly=True, copy=False)
    has_two_options = fields.Boolean(string='2 Sourcing Options Provided', tracking=True)
    sourcing_on_time = fields.Boolean(string='Sourcing Delivered On Time', tracking=True)
    sourcing_options = fields.Text(string='Sourcing Options', tracking=True)

    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Medium'), ('2', 'High')],
        string='Priority', default='0', tracking=True,
    )
    lead_source = fields.Selection(
        [('referral', 'Referral'), ('repeat', 'Repeat Customer'),
         ('website', 'Website'), ('cold', 'Cold Outreach'), ('other', 'Other')],
        string='Lead Source', tracking=True,
    )
    lost_reason = fields.Text(string='Lost Reason', tracking=True)
    follow_up_date = fields.Date(string='Follow Up Date', tracking=True)
    product_category = fields.Selection(
        [('campervan', 'Campervan / Van'), ('toilet', 'Blackmoa Toilet'),
         ('custom_mfg', 'Custom Manufacturing'), ('sourcing', 'General Sourcing'),
         ('other', 'Other')],
        string='Product Category', tracking=True,
    )

    supplier_a_id = fields.Many2one(
        'res.partner', string='Supplier A — Contact',
        domain="[('supplier_rank','>',0)]", tracking=True,
    )
    supplier_a_details = fields.Text(
        string='Option A — Details (price, MOQ, lead time)', tracking=True,
    )
    supplier_b_id = fields.Many2one(
        'res.partner', string='Supplier B — Contact',
        domain="[('supplier_rank','>',0)]", tracking=True,
    )
    supplier_b_details = fields.Text(
        string='Option B — Details (price, MOQ, lead time)', tracking=True,
    )
    primary_option = fields.Selection(
        [('a', 'Option A — Primary'), ('b', 'Option B — Primary')],
        string='Chosen / Recommended Option', tracking=True,
    )

    brief_commitment = fields.Text(string='Brief Commitment / SLA', tracking=True)
    supplier_lead_time = fields.Char(string='Supplier Lead Time', tracking=True)
    sourcing_eta = fields.Date(string='Sourcing ETA', tracking=True)
    margin_approved = fields.Float(string='Margin %', digits=(5, 2), tracking=True)
    md_notes = fields.Text(string='3P Approval Notes', tracking=True)
    approved_eta = fields.Date(string='Confirmed ETA to Customer', tracking=True)

    # New fields — all have matching DB columns from prior migration
    ball_with = fields.Selection([
        ('growth', 'Ball with Growth Lead'),
        ('delivery', 'Ball with Delivery Lead'),
        ('director', 'Ball with Director'),
    ], string='Ball With', default='growth', tracking=True)

    notification_email_growth = fields.Char(
        string='Growth Lead Email',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param('success_pipeline.growth_email', ''),
    )
    notification_email_delivery = fields.Char(
        string='Delivery Lead Email',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param('success_pipeline.delivery_email', ''),
    )
    brief_sent_flag = fields.Boolean(
        string='Brief Sent', column_name='brief_sent', default=False, tracking=True,
    )
    brief_confirmed_flag = fields.Boolean(
        string='Brief Confirmed', column_name='brief_confirmed', default=False, tracking=True,
    )
    note_lead_in = fields.Text(string='Lead Comments', tracking=True)
    note_delivery_confirmed = fields.Text(string='Delivery Lead Comments', tracking=True)
    note_sourcing = fields.Text(string='Innovation Sourcing Notes', tracking=True)

    @api.model
    def _group_expand_stages(self, stages, domain, order=None):
        return [s[0] for s in self._fields['stage'].selection]

    def _group_expand_innovation_stages(self, stages, domain, order=None):
        return ['ideation','feasibility','sourcing','prototype','scale','launch','validation','established','killed']

    @api.model_create_multi
    def create(self, vals_list):
        today = fields.Date.today()
        for vals in vals_list:
            vals.setdefault('stage_date', today)
            if vals.get('record_type') == 'innovation' and not vals.get('innovation_stage'):
                vals['innovation_stage'] = 'ideation'
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('record_type') == 'innovation' and not vals.get('innovation_stage'):
            for rec in self:
                if not rec.innovation_stage:
                    vals['innovation_stage'] = 'ideation'
                    break
        if 'stage' in vals and not self._context.get('_success_lock'):
            today = fields.Date.today()
            vals = dict(vals, stage_date=today)
        result = super().write(vals)
        if 'stage' in vals and not self._context.get('_success_lock'):
            stage = vals['stage']
            today = fields.Date.today()
            lk = self.with_context(_success_lock=True)
            if stage == 'cso_confirmed':
                lk.filtered(lambda r: not r.date_cso_confirmed).write(
                    {'date_cso_confirmed': today}
                )
            if stage in ('closed_won', 'closed_lost'):
                lk.filtered(lambda r: not r.date_closed).write({'date_closed': today})
        if vals.get('go_no_go') == 'no':
            self.with_context(_success_lock=True).write({'innovation_stage': 'killed'})
        return result


    @api.onchange('record_type')
    def _onchange_record_type(self):
        if self.record_type == 'innovation' and not self.innovation_stage:
            self.innovation_stage = 'ideation'

    @api.onchange('stage')
    def _onchange_stage(self):
        if self.stage in ('closed_won', 'closed_lost') and not self.date_closed:
            self.date_closed = fields.Date.today()

    def action_send_brief(self):
        for rec in self:
            rec.ball_with = 'delivery'
            rec.brief_sent_flag = True
            self.env['mail.mail'].create({
                'subject': f'New Lead Brief — {rec.name}',
                'email_to': rec.notification_email_delivery,
                'body_html': (
                    f'<p>New brief from Growth Lead:</p>'
                    f'<p><b>Customer:</b> {rec.partner_id.name}<br/>'
                    f'<b>Need:</b> {rec.what_they_need or "—"}<br/>'
                    f'<b>Qty:</b> {rec.qty or "—"}<br/>'
                    f'<b>Budget:</b> {rec.budget or "—"}<br/>'
                    f'<b>Deadline:</b> {rec.cso_deadline or "—"}</p>'
                ),
            }).send()
            rec.message_post(body='Brief sent to Delivery Lead by email.')

    def action_reset_brief(self):
        for rec in self:
            rec.ball_with = 'growth'
            rec.brief_sent_flag = False
            rec.message_post(body='Brief reset — editing and resending.')

    def action_confirm_brief(self):
        for rec in self:
            rec.ball_with = 'growth'
            rec.brief_confirmed_flag = True
            rec.stage = 'delivery_lead_confirmed'
            self.env['mail.mail'].create({
                'subject': f'Brief Confirmed — {rec.name}',
                'email_to': rec.notification_email_growth,
                'body_html': (
                    f'<p>Brief confirmed by Delivery Lead.</p>'
                    f'<p><b>Deal:</b> {rec.name}<br/>'
                    f'<b>Customer:</b> {rec.partner_id.name}</p>'
                ),
            }).send()
            rec.message_post(body='Brief confirmed. Stage moved to Delivery Lead Confirmed. Ball back with Growth Lead.')

    def action_reset_confirmation(self):
        for rec in self:
            rec.ball_with = 'delivery'
            rec.brief_confirmed_flag = False
            rec.message_post(body='Confirmation reset by Delivery Lead.')

    def action_confirm_and_send(self):
        self.stage = 'cso_confirmed'

    def action_start_sourcing(self):
        self.stage = 'sourcing'

    def action_send_to_md(self):
        self.stage = 'md_approval'

    def action_close_won(self):
        self.stage = 'closed_won'
        if self.supplier_a_id and self.supplier_rating:
            self.supplier_a_id.write({'comment': (self.supplier_a_id.comment or '') + f'\nRated {self.supplier_rating}/5 on deal {self.name} ({fields.Date.today()})'})

    def action_close_lost(self):
        self.stage = 'closed_lost'

    INNOVATION_STAGES = ['ideation','feasibility','sourcing','prototype','scale','launch','validation','established']

    def action_advance_innovation(self):
        stages = ["ideation","feasibility","sourcing","prototype","scale","launch","validation","established"]
        if self.innovation_stage in stages:
            idx = stages.index(self.innovation_stage)
            if idx < len(stages) - 1:
                self.innovation_stage = stages[idx + 1]
                self.message_post(body=f"Advanced to {stages[idx+1]}")

    def action_kill_innovation(self):
        self.innovation_stage = 'killed'
        self.message_post(body='Innovation killed.')

    def action_create_product_from_lead(self):
        product = self.env['product.template'].create({
            'name': self.new_product_name or self.name,
            'description': self.new_product_description,
            'type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
        })
        self.product_id = product
        self.message_post(body=f'Product created: {product.name}')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'res_id': product.id,
            'view_mode': 'form',
            'target': 'current',
        }


class SuccessPipelineStats(models.Model):
    _name = 'success.pipeline.stats'
    _description = 'Success Pipeline Dashboard'
    _rec_name = 'dashboard_label'
    _auto = True

    dashboard_label = fields.Char(
        string='Name', compute='_compute_dashboard_label', store=False,
    )

    @api.depends()
    def _compute_dashboard_label(self):
        for rec in self:
            rec.dashboard_label = 'Success Pipeline Dashboard'

    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id,
    )

    filter_period = fields.Selection(FILTER_PERIOD, string='Period', default='all')
    filter_product_category = fields.Selection(
        [('all', 'All Categories'),
         ('campervan', 'Campervan / Van'), ('toilet', 'Blackmoa Toilet'),
         ('custom_mfg', 'Custom Manufacturing'), ('sourcing', 'General Sourcing'),
         ('other', 'Other')],
        string='Product Category', default='all',
    )

    leads_this_month = fields.Integer(string='Leads This Month', compute='_compute_kpis')
    leads_status = fields.Selection(STATUS_SEL, string='Leads Status', compute='_compute_kpis')
    briefs_sent = fields.Integer(string='Briefs Sent', compute='_compute_kpis')
    sourcing_count = fields.Integer(string='In Sourcing', compute='_compute_kpis')
    deals_closed = fields.Integer(string='Deals Closed', compute='_compute_kpis')
    revenue_closed = fields.Monetary(
        string='Revenue Closed', compute='_compute_kpis', currency_field='currency_id',
    )
    avg_days_to_close = fields.Float(
        string='Avg Days to Close', digits=(5, 1), compute='_compute_kpis',
    )
    stalled_leads = fields.Integer(string='Stalled 7d+', compute='_compute_kpis')
    stalled_status = fields.Selection(STATUS_SEL, string='Stalled Status', compute='_compute_kpis')
    brief_quality_pct = fields.Float(
        string='Brief Completion %', digits=(5, 1), compute='_compute_kpis',
    )
    brief_quality_status = fields.Selection(STATUS_SEL, string='Brief Status', compute='_compute_kpis')
    outcome_posted_pct = fields.Float(
        string='Outcome Posted %', digits=(5, 1), compute='_compute_kpis',
    )
    outcome_posted_status = fields.Selection(STATUS_SEL, string='Outcome Status', compute='_compute_kpis')
    conversion_rate_pct = fields.Float(
        string='Conversion Rate %', digits=(5, 1), compute='_compute_kpis',
    )
    conversion_status = fields.Selection(STATUS_SEL, string='Conv Status', compute='_compute_kpis')
    cso_response_pct = fields.Float(
        string='Delivery Lead 24hr Response %', digits=(5, 1), compute='_compute_kpis',
    )
    cso_response_status = fields.Selection(STATUS_SEL, string='DL Response Status', compute='_compute_kpis')
    sourcing_on_time_pct = fields.Float(
        string='Sourcing On Time %', digits=(5, 1), compute='_compute_kpis',
    )
    sourcing_on_time_status = fields.Selection(STATUS_SEL, string='On Time Status', compute='_compute_kpis')
    two_options_pct = fields.Float(
        string='Two Options %', digits=(5, 1), compute='_compute_kpis',
    )
    two_options_status = fields.Selection(STATUS_SEL, string='2-Opt Status', compute='_compute_kpis')
    active_leads = fields.Integer(string='Active Leads', compute='_compute_kpis')
    active_leads_status = fields.Selection(STATUS_SEL, string='Active Status', compute='_compute_kpis')
    qoq_revenue_growth_pct = fields.Float(
        string='QoQ Revenue Growth %', digits=(5, 1), compute='_compute_kpis',
    )
    qoq_status = fields.Selection(STATUS_SEL, string='QoQ Status', compute='_compute_kpis')
    sourcing_conversion_pct = fields.Float(
        string='Sourcing Conversion %', digits=(5, 1), compute='_compute_kpis',
    )
    sourcing_conversion_status = fields.Selection(STATUS_SEL, string='Src Conv Status', compute='_compute_kpis')
    avg_sourcing_days = fields.Float(
        string='Avg Days to Confirm', digits=(5, 1), compute='_compute_kpis',
    )
    avg_sourcing_days_status = fields.Selection(STATUS_SEL, string='Avg Days Status', compute='_compute_kpis')

    leads_bar_pct = fields.Integer(string='Leads Bar %', compute='_compute_kpis')
    brief_quality_bar_pct = fields.Integer(string='Brief Quality Bar %', compute='_compute_kpis')
    outcome_posted_bar_pct = fields.Integer(string='Outcome Posted Bar %', compute='_compute_kpis')
    conversion_bar_pct = fields.Integer(string='Conversion Bar %', compute='_compute_kpis')
    qoq_bar_pct = fields.Integer(string='QoQ Bar %', compute='_compute_kpis')
    cso_response_bar_pct = fields.Integer(string='CSO Response Bar %', compute='_compute_kpis')
    sourcing_on_time_bar_pct = fields.Integer(string='Sourcing On Time Bar %', compute='_compute_kpis')
    two_options_bar_pct = fields.Integer(string='Two Options Bar %', compute='_compute_kpis')
    sourcing_conversion_bar_pct = fields.Integer(string='Sourcing Conv Bar %', compute='_compute_kpis')
    avg_sourcing_bar_pct = fields.Integer(string='Avg Sourcing Bar %', compute='_compute_kpis')

    active_game_changers = fields.Integer(string='Active Game-Changers', compute='_compute_kpis')
    launched_game_changers = fields.Integer(string='Launched Game-Changers', compute='_compute_kpis')

    cgo_nn_week = fields.Char(
        string='Week of', default=lambda self: fields.Date.today().strftime('%d %b %Y'),
    )
    cgo_nn1_done = fields.Boolean(string='Growth Lead: Daily client response')
    cgo_nn2_done = fields.Boolean(string='Growth Lead: Market visits (4 days/week)')
    cgo_nn3_done = fields.Boolean(string='Growth Lead: Read customer psychology article')
    cso_nn1_done = fields.Boolean(string='Delivery Lead: Confirm brief within 24hr')
    cso_nn2_done = fields.Boolean(string='Delivery Lead: Deliver 2 options always')
    cso_nn3_done = fields.Boolean(string='Delivery Lead: Never miss ETA without update')

    cgo_nn1_text = fields.Char(string='GL Commitment 1', default='Daily client response — respond same day')
    cgo_nn2_text = fields.Char(string='GL Commitment 2', default='Market visits — minimum 4 days this week')
    cgo_nn3_text = fields.Char(string='GL Commitment 3', default='Read one customer psychology article this week')
    cso_nn1_text = fields.Char(string='DL Commitment 1', default='Confirm every brief within 24hr')
    cso_nn2_text = fields.Char(string='DL Commitment 2', default='Deliver 2 sourcing options — never 1')
    cso_nn3_text = fields.Char(string='DL Commitment 3', default='Never go silent past ETA — post update first')

    sim_leads_target = fields.Integer(string='Leads target / month', default=10)
    sim_response_target = fields.Integer(string='Delivery Lead response target %', default=80)
    sim_conversion_target = fields.Integer(string='Conversion target %', default=30)

    def _s(self, actual, target, higher=True, tol=0.10):
        if target == 0:
            return 'on_track' if actual == 0 else 'off_track'
        ratio = actual / float(target)
        if higher:
            if ratio >= 1.0:
                return 'on_track'
            return 'near_miss' if ratio >= (1.0 - tol) else 'off_track'
        else:
            if actual == 0:
                return 'on_track'
            return 'near_miss' if actual <= target * (1.0 + tol) else 'off_track'

    def _period_domain(self):
        today = fields.Date.today()
        period = self.filter_period or 'all'
        base = [('record_type', '=', 'inquiry')]
        if period == 'this_month':
            return base + [('date_created', '>=', today.replace(day=1))]
        elif period == 'this_quarter':
            q = (today.month - 1) // 3
            return base + [('date_created', '>=', today.replace(month=q * 3 + 1, day=1))]
        elif period == 'this_year':
            return base + [('date_created', '>=', today.replace(month=1, day=1))]
        return base

    def _cat_domain(self):
        cat = self.filter_product_category or 'all'
        if cat and cat != 'all':
            return [('product_category', '=', cat)]
        return []

    @api.depends('filter_period', 'filter_product_category')
    def _compute_kpis(self):
        Lead = self.env['success.lead']
        today = fields.Date.today()
        first_day = today.replace(day=1)
        stall_cutoff = today - timedelta(days=7)
        q = (today.month - 1) // 3
        this_q_start = today.replace(month=q * 3 + 1, day=1)
        if q == 0:
            last_q_start = today.replace(year=today.year - 1, month=10, day=1)
            last_q_end = today.replace(year=today.year - 1, month=12, day=31)
        else:
            lqm = q * 3
            last_q_start = today.replace(month=(q - 1) * 3 + 1, day=1)
            last_q_end = today.replace(month=lqm, day=cal.monthrange(today.year, lqm)[1])

        for rec in self:
            base = rec._period_domain() + rec._cat_domain()
            all_leads = Lead.search(base)
            total = len(all_leads)
            active = all_leads.filtered(lambda r: r.stage not in ('closed_won', 'closed_lost'))
            this_month = Lead.search(base + [('date_created', '>=', first_day)])
            closed_won = all_leads.filtered(lambda r: r.stage == 'closed_won')
            closed_all = all_leads.filtered(lambda r: r.stage in ('closed_won', 'closed_lost'))
            stalled = all_leads.filtered(
                lambda r: r.stage not in ('closed_won', 'closed_lost')
                and r.stage_date and r.stage_date <= stall_cutoff
            )
            sourcing_reached = all_leads.filtered(
                lambda r: r.stage in ('sourcing', 'md_approval', 'closed_won', 'closed_lost')
            )
            cso_tracked = all_leads.filtered(lambda r: r.date_cso_confirmed)
            this_q_rev = sum(all_leads.filtered(
                lambda r: r.stage == 'closed_won' and r.date_closed and r.date_closed >= this_q_start
            ).mapped('deal_value'))
            last_q_rev = sum(Lead.search(base + [
                ('stage', '=', 'closed_won'),
                ('date_closed', '>=', last_q_start),
                ('date_closed', '<=', last_q_end),
            ]).mapped('deal_value'))
            sourcing_or_beyond = all_leads.filtered(
                lambda r: r.stage in ('sourcing', 'md_approval', 'closed_won', 'closed_lost')
            )
            sourcing_won = all_leads.filtered(
                lambda r: r.stage == 'closed_won' and r.date_cso_confirmed
            )

            rec.leads_this_month = len(this_month)
            rec.leads_status = self._s(len(this_month), 10)
            rec.briefs_sent = len(all_leads.filtered(lambda r: r.brief_sent_flag))
            rec.sourcing_count = len(all_leads.filtered(lambda r: r.stage == 'sourcing'))
            rec.deals_closed = len(closed_won)
            rec.revenue_closed = sum(closed_won.mapped('deal_value'))
            days_list = [
                (r.date_closed - r.date_created).days
                for r in closed_won if r.date_closed and r.date_created
            ]
            rec.avg_days_to_close = sum(days_list) / len(days_list) if days_list else 0.0
            rec.stalled_leads = len(stalled)
            rec.stalled_status = self._s(len(stalled), 0, higher=False)

            def _brief_fields_filled(r):
                return sum([
                    bool(r.what_they_need),
                    bool(r.budget),
                    bool(r.timeline),
                    bool(r.cso_deadline),
                ])
            total_filled = sum(_brief_fields_filled(r) for r in all_leads)
            rec.brief_quality_pct = total_filled / (total * 4) * 100 if total else 0.0
            rec.brief_quality_status = self._s(rec.brief_quality_pct, 80)

            closed_with_notes = closed_all.filtered(
                lambda r: r.outcome_notes and r.outcome_notes.strip()
            )
            rec.outcome_posted_pct = (
                len(closed_with_notes) / len(closed_all) * 100 if closed_all else 0.0
            )
            rec.outcome_posted_status = self._s(rec.outcome_posted_pct, 100)

            rec.conversion_rate_pct = len(closed_won) / total * 100 if total else 0.0
            rec.conversion_status = self._s(rec.conversion_rate_pct, 30)

            ct = len(cso_tracked)
            rec.cso_response_pct = ct / total * 100 if total else 0.0
            rec.cso_response_status = self._s(rec.cso_response_pct, 80)

            st = len(sourcing_reached)
            rec.sourcing_on_time_pct = (
                len(sourcing_reached.filtered(lambda r: r.sourcing_on_time)) / st * 100
                if st else 0.0
            )
            rec.sourcing_on_time_status = self._s(rec.sourcing_on_time_pct, 90)
            rec.two_options_pct = (
                len(sourcing_reached.filtered(lambda r: r.has_two_options)) / st * 100
                if st else 0.0
            )
            rec.two_options_status = self._s(rec.two_options_pct, 100)

            rec.active_leads = len(active)
            rec.active_leads_status = self._s(len(active), 10)

            if last_q_rev > 0:
                rec.qoq_revenue_growth_pct = (this_q_rev - last_q_rev) / last_q_rev * 100
            else:
                rec.qoq_revenue_growth_pct = 0.0 if this_q_rev == 0 else 100.0
            rec.qoq_status = self._s(rec.qoq_revenue_growth_pct, 15)

            sob = len(sourcing_or_beyond)
            rec.sourcing_conversion_pct = len(sourcing_won) / sob * 100 if sob else 0.0
            rec.sourcing_conversion_status = self._s(rec.sourcing_conversion_pct, 40)

            avg_days_list = [
                (r.date_cso_confirmed - r.date_created).days
                for r in cso_tracked if r.date_cso_confirmed and r.date_created
            ]
            rec.avg_sourcing_days = (
                sum(avg_days_list) / len(avg_days_list) if avg_days_list else 0.0
            )
            asd = rec.avg_sourcing_days
            if asd < 2.0:
                rec.avg_sourcing_days_status = 'on_track'
            elif asd <= 3.0:
                rec.avg_sourcing_days_status = 'near_miss'
            else:
                rec.avg_sourcing_days_status = 'off_track'

            rec.active_game_changers = Lead.search_count([('record_type','=','innovation'),('innovation_stage','not in',['launch','killed','established'])])
            rec.launched_game_changers = Lead.search_count([('record_type','=','innovation'),('innovation_stage','in',['launch','validation','established'])])
            rec.leads_bar_pct = min(100, max(0, round(rec.leads_this_month / 10.0 * 100)))
            rec.brief_quality_bar_pct = min(100, max(0, round(rec.brief_quality_pct)))
            rec.outcome_posted_bar_pct = min(100, max(0, round(rec.outcome_posted_pct)))
            rec.conversion_bar_pct = min(100, max(0, round(rec.conversion_rate_pct)))
            rec.qoq_bar_pct = min(100, max(0, round(rec.qoq_revenue_growth_pct / 15.0 * 100)))
            rec.cso_response_bar_pct = min(100, max(0, round(rec.cso_response_pct)))
            rec.sourcing_on_time_bar_pct = min(100, max(0, round(rec.sourcing_on_time_pct)))
            rec.two_options_bar_pct = min(100, max(0, round(rec.two_options_pct)))
            rec.sourcing_conversion_bar_pct = min(100, max(0, round(rec.sourcing_conversion_pct)))
            rec.avg_sourcing_bar_pct = min(100, max(0, round(2.0 / max(rec.avg_sourcing_days, 0.1) * 100)))

    def action_view_leads_month(self):
        today = fields.Date.today()
        return {
            'type': 'ir.actions.act_window', 'name': 'Leads This Month',
            'res_model': 'success.lead', 'view_mode': 'kanban,list,form',
            'domain': [('date_created', '>=', str(today.replace(day=1)))],
        }

    def action_view_briefs(self):
        return {
            'type': 'ir.actions.act_window', 'name': 'Briefs Sent',
            'res_model': 'success.lead', 'view_mode': 'kanban,list,form',
            'domain': [('brief_sent_flag', '=', True)],
        }

    def action_view_sourcing(self):
        return {
            'type': 'ir.actions.act_window', 'name': 'Sourcing Active',
            'res_model': 'success.lead', 'view_mode': 'kanban,list,form',
            'domain': [('stage', '=', 'sourcing')],
        }

    def action_view_closed(self):
        return {
            'type': 'ir.actions.act_window', 'name': 'Deals Closed',
            'res_model': 'success.lead', 'view_mode': 'kanban,list,form',
            'domain': [('stage', '=', 'closed_won')],
        }

    def action_view_revenue(self):
        return {
            'type': 'ir.actions.act_window', 'name': 'Revenue — Closed Won',
            'res_model': 'success.lead', 'view_mode': 'list,form',
            'domain': [('stage', '=', 'closed_won')],
        }

    def action_view_stalled(self):
        cutoff = fields.Date.today() - timedelta(days=7)
        return {
            'type': 'ir.actions.act_window', 'name': 'Stalled Leads',
            'res_model': 'success.lead', 'view_mode': 'list,kanban,form',
            'domain': [
                ('stage', 'not in', ['closed_won', 'closed_lost']),
                ('stage_date', '<=', str(cutoff)),
            ],
        }

    def action_view_avg_close(self):
        return {
            'type': 'ir.actions.act_window', 'name': 'Closed Deals',
            'res_model': 'success.lead', 'view_mode': 'list,form',
            'domain': [('stage', '=', 'closed_won'), ('date_closed', '!=', False)],
        }

    @api.model
    def get_or_create_singleton(self):
        record = self.search([], limit=1, order='id asc')
        if not record:
            record = self.create({})
        return record.id

    @api.model
    def open_singleton_dashboard(self):
        record = self.search([], limit=1, order='id asc')
        if not record:
            record = self.create({})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Success Pipeline Dashboard',
            'res_model': 'success.pipeline.stats',
            'res_id': record.id,
            'views': [(False, 'form')],
            'view_mode': 'form',
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        }


class SuccessPipelineSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    success_growth_email = fields.Char(string='Growth Lead Email', config_parameter='success_pipeline.growth_email')
    success_delivery_email = fields.Char(string='Delivery Lead Email', config_parameter='success_pipeline.delivery_email')
