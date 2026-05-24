import { useState } from 'react'
import './App.css'

type CaseId = 'DA0208' | 'DA0003'

type CaseData = {
  id: CaseId
  intent: string
  expectedVsGot: string[]
}

const CASES: CaseData[] = [
  {
    id: 'DA0208',
    intent:
      'Find the minimum uniform box size for packing cowbells with at most 2 per box and at most k boxes.',
    expectedVsGot: ['Expected 5, got 0', 'Expected 10, got 0', 'Expected 10, got 0'],
  },
  {
    id: 'DA0003',
    intent: 'Maximize total chocolates under divisibility and overlap rules.',
    expectedVsGot: ['Expected 13, got 0', 'Expected 28, got 0', 'Expected 32, got 0'],
  },
]

const EVIDENCE_CARDS = [
  '2,334 Dafny records',
  '1,448 useful NL descriptions',
  '128 scanner candidates',
  '41 high-confidence candidates adjudicated',
  '11 validated demonstrations',
  '2 direct-Dafny cases',
  '2 repaired-target blocks',
]

const BAD_CANDIDATE = `method Solve(...) returns (result: int)\n  ensures result >= 0\n{\n  result := 0;\n}`

function App() {
  const [activeCaseId, setActiveCaseId] = useState<CaseId>('DA0208')
  const [showVerified, setShowVerified] = useState(false)
  const [showExamples, setShowExamples] = useState(false)
  const [showRepaired, setShowRepaired] = useState(false)

  const activeCase = CASES.find((demoCase) => demoCase.id === activeCaseId)

  if (!activeCase) {
    return null
  }

  const switchCase = (caseId: CaseId) => {
    setActiveCaseId(caseId)
    setShowVerified(false)
    setShowExamples(false)
    setShowRepaired(false)
  }

  return (
    <main className="page">
      <header className="hero">
        <p className="artifact-label">Research Artifact Demo</p>
        <h1>Verified but Wrong Demo</h1>
        <p className="subtitle">
          Vericoding can prove that code satisfies a formal specification. But
          was the specification the right target?
        </p>
      </header>

      <section className="panel">
        <h2>Main demo cases</h2>
        <p className="panel-copy">
          Candidate verifies against a public formal target while failing intended
          behavior.
        </p>

        <div className="tab-row" role="tablist" aria-label="Select case">
          {CASES.map((demoCase) => (
            <button
              key={demoCase.id}
              type="button"
              role="tab"
              aria-selected={activeCase.id === demoCase.id}
              className={`tab ${activeCase.id === demoCase.id ? 'active' : ''}`}
              onClick={() => switchCase(demoCase.id)}
            >
              {demoCase.id}
            </button>
          ))}
        </div>

        <ol className="steps">
          <li>
            <h3>Step 1: Natural-language intent</h3>
            <p>{activeCase.intent}</p>
          </li>

          <li>
            <h3>Step 2: Public formal target</h3>
            <p>
              For both Tier 1 cases, the public target effectively only requires
              a nonnegative result:
            </p>
            <pre className="target-block">
              <code>ensures result {'>='} 0</code>
            </pre>
          </li>

          <li>
            <h3>Step 3: Bad candidate</h3>
            <pre>
              <code>{BAD_CANDIDATE}</code>
            </pre>
          </li>

          <li>
            <h3>Step 4: Verify against public target</h3>
            <button type="button" className="action" onClick={() => setShowVerified(true)}>
              Verify against public target
            </button>
            {showVerified ? (
              <p className="status verified">Dafny 4.11.0: verified, 0 errors</p>
            ) : null}
            <p className="note">
              Replay only: this output is shown from repository reproduction logs,
              not from live browser-side Dafny execution.
            </p>
          </li>

          <li>
            <h3>Step 5: Run intended examples</h3>
            <button type="button" className="action" onClick={() => setShowExamples(true)}>
              Run intended examples
            </button>
            {showExamples ? (
              <ul className="results">
                {activeCase.expectedVsGot.map((entry) => (
                  <li key={entry}>{entry}</li>
                ))}
              </ul>
            ) : null}
          </li>

          <li>
            <h3>Step 6: Apply repaired target</h3>
            <button type="button" className="action" onClick={() => setShowRepaired(true)}>
              Apply repaired target
            </button>
            {showRepaired ? (
              <>
                <p className="status repaired">
                  Bad candidate blocked by repaired target.
                </p>
                <p className="conclusion">
                  This is verified-but-wrong: implementation validity passes, but
                  target validity fails.
                </p>
              </>
            ) : null}
          </li>
        </ol>
      </section>

      <section className="panel">
        <h2>Evidence stack</h2>
        <div className="cards">
          {EVIDENCE_CARDS.map((card) => (
            <article key={card} className="card">
              {card}
            </article>
          ))}
        </div>
      </section>

      <section className="panel">
        <h2>What this demo does and does not show</h2>
        <p>
          This demo replays two Tier 1 direct-Dafny cases from the repository.
          It does not estimate prevalence across all vericoding benchmarks. The
          narrow claim is that target-validity failures can occur when the
          supplied formal target omits intent-critical requirements.
        </p>
      </section>

      <section className="panel">
        <h2>Reproduction commands</h2>
        <pre>
          <code>{`python run_all_repro.py\npython run_external_replication.py`}</code>
        </pre>
      </section>

      <section className="panel">
        <h2>Links</h2>
        <ul className="links">
          <li>
            <a href="https://github.com/your-org/your-repo" target="_blank" rel="noreferrer">
              GitHub repository
            </a>
          </li>
          <li>
            <a href="https://example.com/paper.pdf" target="_blank" rel="noreferrer">
              Paper PDF
            </a>
          </li>
        </ul>
      </section>
    </main>
  )
}

export default App