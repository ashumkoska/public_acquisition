from odoo import api, models, fields, _
from odoo.exceptions import UserError
import datetime


class AcquisitionPlan(models.Model):
    
    _name = 'acquisition.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Acquisition Plan'
    
    # TODO: vo koi sostojbi da bide editable?
    # TODO: dali ddv ke se zemi vo predvid?
    name = fields.Char(string='Title', required=True, track_visibility='always')
    user_id = fields.Many2one('res.users', string='User', readonly=True, default=lambda self: self.env.user, 
                              track_visibility='on_change')
    plan_line_ids = fields.One2many('acquisition.plan.line', 'plan_id', string='Acquisition Plan Items', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id, 
                                  track_visibility='on_change')
    estimated_budget = fields.Monetary(string='Total Estimated Budget', compute='compute_estimated_budget', store=True,
                                       track_visibility='always')
    description = fields.Html(string='Technical Specification')
    plan_date = fields.Date(string='Date', default=fields.Date.today())
    # TODO: moze da bide i broj na denovi, pa avtomatski datumot da se presmeta otkako ke se potvrdi planot
    complaint_deadline = fields.Date(string='Complaint Deadline')
    state_before_complaint = fields.Char(string='State Before Complaint', readonly=True)
    state = fields.Selection([('draft', 'Draft'), 
                              ('submit', 'Submitted'), 
                              ('offers', 'Offers'), 
                              ('auction', 'Auction'), 
                              ('decision', 'Decision'),
                              ('waiting', 'Waiting for Approval'), 
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled'), 
                              ('archive', 'Archive'), 
                              ('complaint', 'Complaint'), 
                              ('contract', 'Contract'), 
                              ('done', 'Done')], string='Status', default='draft', track_visibility='on_change')
    color = fields.Integer(string='Color Index')
    # attachment_ids = fields.One2many('ir.attachment', compute='compute_attachment_ids', string='Main Attachments',
    #                                  help="Attachment that don't come from message.")
    offer_ids = fields.One2many('acquisition.offer', 'acq_plan_id', string='Offers')
    offers_count = fields.Integer(string='Number of Offers', compute='compute_offers_count', store=True)
    com_member_ids = fields.One2many('commission.member', 'acq_plan_id', string='Commission Members')
    
    @api.multi
    @api.depends('plan_line_ids', 'plan_line_ids.quantity', 'plan_line_ids.unit_price')
    def compute_estimated_budget(self):
        for rec in self:
            rec.estimated_budget = sum([line.total_price for line in rec.plan_line_ids])
            
    @api.multi
    @api.depends('offer_ids')
    def compute_offers_count(self):
        for rec in self:
            rec.offers_count = len(rec.offer_ids)
            
    @api.multi
    def submit(self):
        for rec in self:
            rec.write({'state': 'submit'})
    
    @api.multi
    def accept_offers(self):
        for rec in self:
            rec.write({'state': 'offers'})

    @api.multi
    def auction(self):
        for rec in self:
            rec.write({'state': 'auction'})
            
    @api.multi
    def decision(self):
        for rec in self:
            rec.write({'state': 'decision'})
            
    @api.multi
    def approve(self):
        for rec in self:
            rec.write({'state': 'approve'})
            
    @api.multi
    def cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})
            
    @api.multi
    def archive(self):
        for rec in self:
            rec.write({'state': 'archive'})
            
    @api.multi
    def complaint(self):
        for rec in self:
            rec.write({
                'state_before_complaint': rec.state,
                'state': 'complaint'
            })
            
    @api.multi
    def contract(self):
        for rec in self:
            rec.write({'state': 'contract'})
            
    @api.multi
    def done(self):
        for rec in self:
            rec.write({'state': 'done'})
            
    @api.multi
    def submit_to_commision(self):
        for rec in self:
            if not rec.com_member_ids:
                raise UserError(_('Please select the commission members for this acquisition plan!'))
            res_model = self.env['ir.model'].search([('model', '=', 'acquisition.plan')])
            todo_activity_type = self.env.ref('mail.mail_activity_data_todo')
            today = datetime.date.today()
            date_deadline = today + datetime.timedelta(days=7)
            for member in rec.com_member_ids:
                activity_vals = {
                    'res_model_id': res_model.id,
                    'res_id': rec.id,
                    'activity_type_id': todo_activity_type.id,
                    'summary': _('Acquisition Plan Approval'),
                    'date_deadline': date_deadline,
                    'user_id': member.user_id.id,
                    'note': _('This acquisition plan needs to be signed by each of the commission members.')
                }
                activity_id = self.env['mail.activity'].create(activity_vals)
                rec.message_subscribe_users([member.user_id.id])
                member.write({
                    'activity_id': activity_id.id
                })
            rec.write({'state': 'waiting'})
            
    @api.model
    def acq_plan_complaint_expired(self):
        active_plans = self.env['acquisition.plan'].search([('state', 'in', ['complaint']),
                                                            ('complaint_deadline', '=', fields.Date.today())])
        for plan in active_plans:
            if plan.state_before_complaint in ['approve', 'archive']:
                plan.write({'state': 'contract'})
            elif plan.state_before_complaint in ['cancel']:
                plan.write({'state': 'done'})

    
class AcquisitionPlanLine(models.Model):
    
    _name = 'acquisition.plan.line'    
    
    name = fields.Char(string='Description', required=True)
    plan_id = fields.Many2one('acquisition.plan', string='Acquisition Plan', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product/Service')
    type_id = fields.Many2one('acquisition.plan.line.type', string='Type')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    unit_price = fields.Monetary(string='Estimated Unit Price')
    total_price = fields.Monetary(string='Total', compute='compute_total_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='plan_id.currency_id')
    sequence = fields.Integer(string='Sequence', default=10)
    
    @api.multi
    @api.depends('quantity', 'unit_price')
    def compute_total_price(self):
        for rec in self:
            rec.total_price = rec.quantity * rec.unit_price
            
    @api.multi
    @api.onchange('product_id')
    def on_change_product_id(self):
        for rec in self:
            self.name = self.product_id.name
   
    
class AcquisitionPlanLineType(models.Model):
    
    _name = 'acquisition.plan.line.type'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
