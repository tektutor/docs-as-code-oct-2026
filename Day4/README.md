# Day 4

## Info - What is ALM ?
<pre>
- Application Lifecycle Management
- is how a team manages software from the first idea to retirement. 
- An ALM tool keeps these in one place, linked to each other:
  - Requirements: what the software must do
  - Design: how it will do it
  - Development work: tasks, user stories, commits
  - Tests: test cases, test runs and results
  - Defects: bugs and their fixes
  - Releases and changes: versions, baselines and change requests
  - Risks and reviews: who approved what, and when

- The main value is traceability. 
- An auditor can start at a requirement and follow the links to the code, 
  the tests, and the last test result. 
- Standards such as ISO 26262 for cars, IEC 62304 for medical devices and DO-178C 
  for aircraft software demand exactly this.

- ALM tools 
  - PTC Codebeamer
  - Siemens Polarion
  - IBM Engineering Lifecycle Management (DOORS Next), and 
  - Jira with test and requirement add-ons
</pre>

## Info - What is PLM ?
<pre>
- Product Lifecycle Management
- does the same job for the physical product
  - mechanical parts
  - electronics and manufacturing. 
- A PLM tool manages:
  - CAD models and drawings
  - The bill of materials (BOM): which parts make up the product
  - Engineering change orders: approved changes to parts or drawings
  - Suppliers, costs and compliance: RoHS, REACH and similar regulations
  - Manufacturing data: how and where the product is built
  - Service: spare parts and field issues

- PLM
  - Windchill
  - Siemens Teamcenter
  - Dassault 3DEXPERIENCE (ENOVIA), and 
  - SAP PLM

- The difference 
  - ALM manages software and its requirements, tests and changes. 
  - PLM manages hardware and its parts, drawings and production.

- Why the two meet ?
  - a modern product is both
  - Consider a Car battery management system, it involves hardware and software
</pre>

## Info - CodeBeamer Overview
<pre>
- Codebeamer is an Agile Application Lifecycle Management (ALM) solution for distributed development.
- Codebeamer provides management tools for 
  - projects
  - tasks
  - requirements
  - tests
  - changes 
  - configurations
  - builds 
  - documents in a single, secure environment
  - It enables software and hardware development to be more collaborative, transparent, and productive.
</pre>

## Info - PTC CodeBeamer Terminologies
<pre>
- Project
- Trackers
- Item
- Document
- Wiki
- Release
- Sprint
- Traceability Report
- Risk Matrix Diagram
- Severity
- Entities
- Baselines
- Associations
</pre>

## Info - CodeBeamer Projects
<pre>
- Projects are secure, collaborative workplaces where data is organized in Codebeamer. 
- Users can collectively contribute, discuss, share, control the access to information, authenticate, 
  coordinate, plan, and find information through a project. 
- Projects are grouped according to the business type, or functions, such as R&D or Finance.
- A registered Codebeamer user can create a new project if they have sufficient permissions.
</pre>

## Info - CodeBeamer Trackers
<pre>
- are essential item containers in Codebeamer similar to tables in a relational database or 
  classes in object-oriented programming. 
- shape or determine the behaviors, permissions, workflows, escalation rules and notifications 
  of the application. 
- registered user with required permissions can configure several types of trackers in 
  Codebeamer such as A sprint is any non-top-level item in a release-type tracker.Requirements, Tasks, Bugs, Change requests, Releases, Risks and Test cases.
</pre>

## Info - CodeBeamer Item
<pre>
- issues to be addressed for successful project completion according to the project plan.
- examples
  - Customer requirements
  - User Stories
  - Risks
  - Tasks
  - Test sets
  - Test cases
  - Teams
  - Releases, etc.,
</pre>

## Info - CodeBeamer Document
<pre>
- can be an attachment, a comment, user details records, access control and permissions records 
  which can be in any format such as Microsoft Word, Microsoft Excel, RTF, PDF, HTML, Wiki and 
  Text documents. 
- Documents can be shared, uploaded, downloaded, browsed, versioned, approved and tracked.
</pre>

## Info - CodeBeamer Wiki
<pre>
- A Wiki on Codebeamer is a type of persistent object intended to store information, different from trackers, 
  items, and documents.
</pre>

## Info - CodeBeamer Release
<pre>
- A Release is any top-level item in a release-type tracker. 
- By default, each project has one release tracker.
</pre>

## Info - CodeBeamer Sprint
<pre>
- is any non-top-level item in a release-type tracker.
</pre>

## Info - Traceability Report
<pre>
- A table that correlates multiple sets of different trackers or tracker types in a required order  
- displays the dependencies 
  - downstream or 
  - upstream associations or 
  - references between the items 
</pre>

## Info - Risk Matrix Diagram
<pre>
- displays the number of requirement items based on the likelihood and severity values of the associated 
  risks in the form of a matrix
- Y-axis representing Likelihood values and 
- X-axis representing Severity values
</pre>

## Info - Severity
<pre>
- The extent of damage or the degree of risk associated with a particular task, item, or work item (tracker).
</pre>

## Info - Baselines
<pre>
- reflect the current state of an item at a given or specific time in an ongoing project. 
- Baselines are snapshots but not copies of the items.
</pre>

## Info - Associations
<pre>
- are ad-hoc relations created between other Codebeamer entities or external web resources 
  which do not possess a defined value set, severity, or permissions.
</pre>
