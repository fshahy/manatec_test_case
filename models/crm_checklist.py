from odoo import models, fields, api


class CrmChecklistTemplate(models.Model):
    _name = "crm.checklist.template"
    _description = "CRM lead checklist template"

    name = fields.Text(string="Checklist Template")
    active = fields.Boolean(default=True)


class CrmChecklistItem(models.Model):
    _name = "crm.checklist.item"
    _description = "CRM lead checklist item"

    lead_id = fields.Many2one(comodel_name="crm.lead", string="Lead", required=True)
    checklist_template_id = fields.Many2one(comodel_name="crm.checklist.template", required=True)
    done = fields.Boolean(string="Done?")


class CrmLead(models.Model):
    _inherit = "crm.lead"

    checklist_item_ids = fields.One2many("crm.checklist.item", "lead_id", string="Items")
    progress = fields.Integer(compute='_compute_progress', string="Progress (%)")

    @api.depends('progress')
    def _compute_progress(self):
        for rec in self:
            total_items = len(rec.checklist_item_ids)
            if total_items == 0:
                rec.progress = 0
            else:
                items_done = len([item for item in rec.checklist_item_ids if item.done == True])
                rec.progress = (items_done / total_items) * 100

    @api.model_create_multi
    def create(self, vals):
        lead = super(CrmLead, self).create(vals)
        templates = self.env['crm.checklist.template'].search([])

        for template in templates:
            item = self.env['crm.checklist.item'].create({
                'lead_id': lead.id,
                'checklist_template_id': template.id,

            })
            lead.write({
                'checklist_item_ids': [(4, item.id)]
            })

        return lead
