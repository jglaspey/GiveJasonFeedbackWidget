# ABOUTME: SQLite knowledge base for storing learning experiment results
# ABOUTME: Tracks features, experiments, patterns, gotchas, and best practices

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class KnowledgeBase:
    """SQLite-backed knowledge base for autonomous learning."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).parent / "knowledge_base.db"
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database with schema."""
        conn = sqlite3.connect(self.db_path)
        conn.executescript('''
            -- Features being learned
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                confidence_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Individual experiments/tests
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY,
                feature_id INTEGER NOT NULL,
                hypothesis TEXT NOT NULL,
                configuration TEXT NOT NULL,
                expected_outcome TEXT,
                actual_outcome TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            );

            -- Patterns discovered
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY,
                feature_id INTEGER NOT NULL,
                pattern_name TEXT NOT NULL,
                description TEXT NOT NULL,
                evidence TEXT,
                confidence_score REAL DEFAULT 0.0,
                examples TEXT,
                edge_cases TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            );

            -- Gotchas and pitfalls discovered
            CREATE TABLE IF NOT EXISTS gotchas (
                id INTEGER PRIMARY KEY,
                feature_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                how_to_avoid TEXT,
                severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            );

            -- Best practices learned
            CREATE TABLE IF NOT EXISTS best_practices (
                id INTEGER PRIMARY KEY,
                feature_id INTEGER NOT NULL,
                practice TEXT NOT NULL,
                rationale TEXT,
                when_to_use TEXT,
                examples TEXT,
                confidence_score REAL DEFAULT 0.0,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            );
        ''')
        conn.commit()
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Feature operations
    def add_feature(self, name: str, description: str, category: str) -> int:
        """Add a new feature to learn about. Returns feature ID."""
        conn = self._get_conn()
        cursor = conn.execute(
            "INSERT INTO features (name, description, category) VALUES (?, ?, ?)",
            (name, description, category)
        )
        feature_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return feature_id

    def get_feature(self, name: str) -> Optional[dict]:
        """Get feature by name."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM features WHERE name = ?", (name,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_or_create_feature(self, name: str, description: str, category: str) -> int:
        """Get existing feature or create new one. Returns feature ID."""
        feature = self.get_feature(name)
        if feature:
            return feature['id']
        return self.add_feature(name, description, category)

    def update_feature_confidence(self, feature_id: int, confidence: float):
        """Update feature confidence score."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE features SET confidence_score = ?, updated_at = ? WHERE id = ?",
            (confidence, datetime.now(), feature_id)
        )
        conn.commit()
        conn.close()

    # Experiment operations
    def add_experiment(
        self,
        feature_id: int,
        hypothesis: str,
        configuration: dict,
        expected_outcome: str,
        actual_outcome: str,
        success: bool,
        notes: str = ""
    ) -> int:
        """Record an experiment. Returns experiment ID."""
        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO experiments
               (feature_id, hypothesis, configuration, expected_outcome,
                actual_outcome, success, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (feature_id, hypothesis, json.dumps(configuration),
             expected_outcome, actual_outcome, success, notes)
        )
        experiment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return experiment_id

    def get_experiments(self, feature_id: int) -> list[dict]:
        """Get all experiments for a feature."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM experiments WHERE feature_id = ? ORDER BY timestamp",
            (feature_id,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Pattern operations
    def add_pattern(
        self,
        feature_id: int,
        pattern_name: str,
        description: str,
        evidence: list[int],
        confidence: float,
        examples: list[str] = None,
        edge_cases: list[str] = None
    ) -> int:
        """Record a discovered pattern. Returns pattern ID."""
        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO patterns
               (feature_id, pattern_name, description, evidence,
                confidence_score, examples, edge_cases)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (feature_id, pattern_name, description, json.dumps(evidence),
             confidence, json.dumps(examples or []), json.dumps(edge_cases or []))
        )
        pattern_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pattern_id

    def get_patterns(self, feature_id: int) -> list[dict]:
        """Get all patterns for a feature."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM patterns WHERE feature_id = ? ORDER BY confidence_score DESC",
            (feature_id,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Gotcha operations
    def add_gotcha(
        self,
        feature_id: int,
        title: str,
        description: str,
        how_to_avoid: str,
        severity: str
    ) -> int:
        """Record a gotcha/pitfall. Returns gotcha ID."""
        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO gotchas
               (feature_id, title, description, how_to_avoid, severity)
               VALUES (?, ?, ?, ?, ?)""",
            (feature_id, title, description, how_to_avoid, severity)
        )
        gotcha_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return gotcha_id

    def get_gotchas(self, feature_id: int) -> list[dict]:
        """Get all gotchas for a feature."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM gotchas WHERE feature_id = ? ORDER BY severity DESC",
            (feature_id,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Best practice operations
    def add_best_practice(
        self,
        feature_id: int,
        practice: str,
        rationale: str,
        when_to_use: str,
        examples: list[str] = None,
        confidence: float = 0.5
    ) -> int:
        """Record a best practice. Returns practice ID."""
        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO best_practices
               (feature_id, practice, rationale, when_to_use, examples, confidence_score)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (feature_id, practice, rationale, when_to_use,
             json.dumps(examples or []), confidence)
        )
        practice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return practice_id

    def get_best_practices(self, feature_id: int) -> list[dict]:
        """Get all best practices for a feature."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM best_practices WHERE feature_id = ? ORDER BY confidence_score DESC",
            (feature_id,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Reporting
    def get_feature_summary(self, feature_name: str) -> dict:
        """Get complete summary of learnings for a feature."""
        feature = self.get_feature(feature_name)
        if not feature:
            return None

        return {
            "feature": feature,
            "experiments": self.get_experiments(feature['id']),
            "patterns": self.get_patterns(feature['id']),
            "gotchas": self.get_gotchas(feature['id']),
            "best_practices": self.get_best_practices(feature['id'])
        }

    def calculate_feature_confidence(self, feature_id: int) -> float:
        """Calculate confidence based on experiment success rate and pattern confidence."""
        conn = self._get_conn()

        # Get experiment success rate
        experiments = conn.execute(
            "SELECT success FROM experiments WHERE feature_id = ?",
            (feature_id,)
        ).fetchall()

        if not experiments:
            return 0.0

        success_rate = sum(1 for e in experiments if e['success']) / len(experiments)

        # Get average pattern confidence
        patterns = conn.execute(
            "SELECT confidence_score FROM patterns WHERE feature_id = ?",
            (feature_id,)
        ).fetchall()

        pattern_confidence = (
            sum(p['confidence_score'] for p in patterns) / len(patterns)
            if patterns else 0.0
        )

        conn.close()

        # Weighted average: 40% experiment success, 60% pattern confidence
        return 0.4 * success_rate + 0.6 * pattern_confidence


if __name__ == "__main__":
    # Quick test
    kb = KnowledgeBase()

    # Add a test feature
    feature_id = kb.get_or_create_feature(
        "skills_invocation",
        "Understanding how and when skills are automatically invoked",
        "claude-code"
    )
    print(f"Feature ID: {feature_id}")

    # Add a test experiment
    exp_id = kb.add_experiment(
        feature_id=feature_id,
        hypothesis="Skills with keyword-rich descriptions invoke more reliably",
        configuration={"skill_name": "test-skill", "description": "minimal"},
        expected_outcome="skill_invoked",
        actual_outcome="skill_not_invoked",
        success=False,
        notes="Minimal description was not enough to trigger invocation"
    )
    print(f"Experiment ID: {exp_id}")

    # Get summary
    summary = kb.get_feature_summary("skills_invocation")
    print(f"Summary: {json.dumps(summary, indent=2, default=str)}")
