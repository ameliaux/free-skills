export const meta = {
  name: 'portfolio-audit-grid',
  description: 'Sharp 4-lens audit of every repo: Developer, Product Designer, Marketing/GTM, Business/Ops',
  phases: [{ title: 'Analyze', detail: '4 specialist lenses on every repo' }],
}

// args: { dir: "~/Projects", projects: ["name1", "name2", ...] }
const DIR = (args && args.dir) || '~/Projects'
const PROJECTS = (args && args.projects) || []

const LENSES = [
  { key: 'developer', role: 'a senior software engineer and architect', focus: 'build state: core functionality, features, bugs, tech debt, test coverage, infra/deploy. What must be built or fixed to make this a solid, shippable product?' },
  { key: 'product', role: 'a senior product designer', focus: 'UX, end-to-end user flows, product completeness, information architecture, polish, and gaps. What is needed for a coherent, usable, delightful product?' },
  { key: 'marketing', role: 'a marketing and go-to-market strategist', focus: 'positioning, target audience, differentiation, launch readiness, channels, and marketing needs. STRATEGY only — actual copy/ad execution happens later.' },
  { key: 'business', role: 'a business and operations strategist', focus: 'revenue/business model, pricing, business plan, and the downstream operational workflow AFTER the MVP: support (emails/helpdesk), feedback loops, analytics, onboarding. What must exist for this to be a real, sustainable product?' },
]

const LENS_SCHEMA = {
  type: 'object',
  properties: {
    assessment: { type: 'string', description: 'sharp expert take on THIS repo through this lens, 2-4 sentences' },
    todos: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          type: { type: 'string', enum: ['feature','core','bug','chore','polish','docs','infra','design','marketing','business','ops'] },
          desc: { type: 'string' },
          priority: { type: 'string', enum: ['high','med','low'] },
          deps: { type: 'string', description: 'dependencies or empty' }
        },
        required: ['title','type','priority']
      }
    }
  },
  required: ['assessment','todos']
}

phase('Analyze')
const results = await parallel(PROJECTS.map(p => () =>
  parallel(LENSES.map(l => () =>
    agent(
`You are ${l.role}. Audit the project at ${DIR}/${p} STRICTLY through your lens — be genuinely sharp, the way a top expert in your field would be.

1. Read the repo's docs (README, CLAUDE.md, docs/, plans/, ROADMAP/TODO/NOTES/CHANGELOG) and skim the code relevant to your discipline to understand the real current state.
2. Focus: ${l.focus}
3. Return a sharp, specific assessment of THIS repo through your lens, plus a concrete todo list (title, type, short desc, priority high/med/low, deps).

Be honest and specific to this repo. If it's a dormant scaffold with little there, say so plainly and keep it short. No generic make-work — only what genuinely matters for this project.`,
      { schema: LENS_SCHEMA, label: `${l.key}:${p}`, phase: 'Analyze' }
    ).then(r => ({ lens: l.key, ...(r || {}) }))
  )).then(lensResults => ({ project: p, lenses: lensResults.filter(Boolean) }))
))
return results.filter(Boolean)
