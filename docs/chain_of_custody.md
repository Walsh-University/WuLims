feature: Chain of Custody (COC) form
app: chainofcustody

models:

ChainOfCustody:
fields:
received_date: DateField(null=true, blank=true)                 # "Date Rec’d in Lab"
gse_job_number: CharField(max_length=64, blank=true)
page_number: PositiveSmallIntegerField(null=true, blank=true)
page_total: PositiveSmallIntegerField(null=true, blank=true)

      # Client Information
      client_name: CharField(max_length=255)
      client_address: TextField(blank=true)
      client_phone: CharField(max_length=64, blank=true)
      client_email: EmailField(blank=true)

      # Project Information
      project_name: CharField(max_length=255, blank=true)
      project_location: CharField(max_length=255, blank=true)
      project_number: CharField(max_length=64, blank=true)
      project_manager: CharField(max_length=255, blank=true)

      # Report information / deliverables
      deliverables_fax: BooleanField(default=false)
      deliverables_email: BooleanField(default=true)
      deliverables_additional: TextField(blank=true)

      # Billing
      billing_same_as_client: BooleanField(default=true)
      billing_name: CharField(max_length=255, blank=true)
      billing_address: TextField(blank=true)
      billing_phone: CharField(max_length=64, blank=true)
      billing_email: EmailField(blank=true)
      purchase_order_number: CharField(max_length=64, blank=true)

      # Turnaround
      tat: CharField(choices=[STANDARD, RUSH], default=STANDARD)
      due_date: DateField(null=true, blank=true)
      due_time: TimeField(null=true, blank=true)

      # Other requirements/comments/detection limits
      requirements_comments: TextField(blank=true)

      # Container / preservative (COC-level defaults)
      container_type: CharField(max_length=128, blank=true)
      preservative: CharField(max_length=128, blank=true)

      created_at: DateTimeField(auto_now_add=true)
      updated_at: DateTimeField(auto_now=true)

Sample:
fields:
chain_of_custody: ForeignKey(ChainOfCustody, related_name="samples", on_delete=CASCADE)

      lab_id: CharField(max_length=64, blank=true)                    # "CSE Lab ID (Lab Use Only)"
      sample_id: CharField(max_length=128)                            # "Sample ID"
      collection_date: DateField(null=true, blank=true)
      collection_time: TimeField(null=true, blank=true)
      sample_matrix: CharField(max_length=128, blank=true)
      sampler_initials: CharField(max_length=16, blank=true)

      # Optional per-sample container/preservative overrides
      container_type: CharField(max_length=128, blank=true)
      preservative: CharField(max_length=128, blank=true)

      notes: TextField(blank=true)

AnalysisMethod:
fields:
code: CharField(max_length=64, unique=true)                     # e.g., "VOC", "Metals", "EPA 8260"
name: CharField(max_length=255)
description: TextField(blank=true)
is_active: BooleanField(default=true)

RequestedAnalysis:
fields:
chain_of_custody: ForeignKey(ChainOfCustody, related_name="requested_analyses", on_delete=CASCADE)
method: ForeignKey(AnalysisMethod, on_delete=PROTECT)

      # This represents the checkbox matrix: which samples are checked for this method
      samples: ManyToManyField(Sample, related_name="requested_methods", blank=true)

      notes: TextField(blank=true)

    constraints:
      unique_together: [chain_of_custody, method]

SampleHandling:
fields:
chain_of_custody: OneToOneField(ChainOfCustody, related_name="handling", on_delete=CASCADE)
chill: BooleanField(default=false)
cool: BooleanField(default=false)
room_temp: BooleanField(default=false)
none_needed: BooleanField(default=false)
dry_ice: BooleanField(default=false)
other: BooleanField(default=false)
other_text: CharField(max_length=255, blank=true)
comments: TextField(blank=true)

CustodyEvent:
fields:
chain_of_custody: ForeignKey(ChainOfCustody, related_name="custody_events", on_delete=CASCADE)
relinquished_by: CharField(max_length=255)
relinquished_at: DateTimeField(null=true, blank=true)
received_by: CharField(max_length=255)
received_at: DateTimeField(null=true, blank=true)

views:
- COC list page (table, search by client/project/job #)
- COC create/edit page:
  sections:
  - header + client + project + billing + turnaround + comments
  - inline formset for Samples (add/remove rows)
  - analysis requested section:
  - show AnalysisMethod rows (active only)
  - for each method, render sample checkboxes (matrix style)
  - custody event inline formset
- COC detail page (read-only, printable)
- Optional: PDF export later

admin:
- register all models
- ChainOfCustody admin includes inlines: SampleInline, CustodyEventInline, RequestedAnalysisInline (or custom UI)
- AnalysisMethod manageable by staff

migrations:
- initial migrations for all models above

tests:
- model creation tests
- requested analysis uniqueness constraint test
- add samples + mark requested analyses test
