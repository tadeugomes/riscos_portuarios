"""
Generate Initial Insights Report for Port Risk Assessment

This script creates a comprehensive insights report based on the processed risk assessment data.
"""

import pandas as pd
import numpy as np
from data_processor import PortRiskDataProcessor
import json
from datetime import datetime
import os

def generate_insights_report():
    """Generate comprehensive insights report"""
    
    print("Generating Port Risk Assessment Insights Report...")
    print("=" * 60)
    
    # Initialize processor and load data
    processor = PortRiskDataProcessor()
    
    try:
        processor.load_data()
        metadata = processor.extract_metadata()
        processed_data = processor.process_risk_data()
        statistics = processor.calculate_risk_statistics()
        
        print(f"✓ Data loaded successfully")
        print(f"  - Total responses: {metadata['total_responses']}")
        print(f"  - Processed risk records: {len(processed_data)}")
        print()
        
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return
    
    # Create outputs directory
    os.makedirs('outputs', exist_ok=True)
    
    # Generate report sections
    report_sections = []
    
    # 1. Executive Summary
    exec_summary = generate_executive_summary(metadata, statistics)
    report_sections.append(exec_summary)
    
    # 2. Risk Landscape Overview
    risk_overview = generate_risk_overview(processed_data, statistics)
    report_sections.append(risk_overview)
    
    # 3. Geographic Analysis
    geo_analysis = generate_geographic_analysis(processed_data, statistics)
    report_sections.append(geo_analysis)
    
    # 4. Port Type Comparison
    port_comparison = generate_port_type_comparison(statistics)
    report_sections.append(port_comparison)
    
    # 5. Time Period Analysis
    time_analysis = generate_time_period_analysis(statistics)
    report_sections.append(time_analysis)
    
    # 6. Top Risk Items
    top_risks = generate_top_risks_analysis(statistics)
    report_sections.append(top_risks)
    
    # 7. Key Recommendations
    recommendations = generate_recommendations(statistics)
    report_sections.append(recommendations)
    
    # Save complete report
    complete_report = "\n\n".join(report_sections)
    
    # Save as text file
    report_path = 'outputs/port_risk_insights_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(complete_report)
    
    # Save as JSON for programmatic access
    json_path = 'outputs/port_risk_insights.json'
    insights_data = {
        'metadata': metadata,
        'statistics': statistics,
        'top_risks_by_category': statistics.get('top_risks', {}),
        'risk_trends': statistics.get('risk_by_time_period', {}),
        'generated_at': datetime.now().isoformat()
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(insights_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✓ Reports generated successfully!")
    print(f"  - Text report: {report_path}")
    print(f"  - JSON data: {json_path}")
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("EXECUTIVE SUMMARY")
    print("=" * 60)
    print(exec_summary)

def generate_executive_summary(metadata, statistics):
    """Generate executive summary section"""
    
    summary = f"""
EXECUTIVE SUMMARY
================

Survey Overview:
- Total Participants: {metadata['total_responses']} port organizations
- Data Collection Period: {metadata['date_range']['start']} to {metadata['date_range']['end']}
- Geographic Coverage: {len(metadata['states'])} Brazilian states
- Organization Types: {len(metadata['port_types'])} different port entity types

Key Findings:
"""
    
    # Overall risk levels
    overall_risks = statistics.get('overall_risk_levels', {})
    if overall_risks:
        highest_risk = max(overall_risks.items(), key=lambda x: x[1] if x[1] is not None else 0)
        lowest_risk = min(overall_risks.items(), key=lambda x: x[1] if x[1] is not None else float('inf'))
        
        summary += f"""
- Highest Risk Category: {highest_risk[0]} (Average Score: {highest_risk[1]:.2f}/5.0)
- Lowest Risk Category: {lowest_risk[0]} (Average Score: {lowest_risk[1]:.2f}/5.0)
"""
    
    # Top states by participation
    top_states = sorted(metadata['states'].items(), key=lambda x: x[1], reverse=True)[:5]
    summary += f"- Top Participating States: {', '.join([state for state, count in top_states])}\n"
    
    # Organization type distribution
    org_types = metadata['port_types']
    dominant_type = max(org_types.items(), key=lambda x: x[1]) if org_types else ("Unknown", 0)
    summary += f"- Most Common Organization Type: {dominant_type[0]} ({dominant_type[1]} responses)\n"
    
    return summary

def generate_risk_overview(processed_data, statistics):
    """Generate risk landscape overview"""
    
    overview = """
RISK LANDSCAPE OVERVIEW
======================

Risk Category Analysis:
"""
    
    overall_risks = statistics.get('overall_risk_levels', {})
    for category, score in overall_risks.items():
        if score is not None:
            risk_level = get_risk_level(score)
            overview += f"- {category}: {score:.2f}/5.0 ({risk_level})\n"
    
    # Risk distribution
    numeric_data = processed_data[
        processed_data['risk_score'].apply(lambda x: isinstance(x, (int, float)))
    ]
    
    if not numeric_data.empty:
        mean_score = numeric_data['risk_score'].mean()
        std_score = numeric_data['risk_score'].std()
        overview += f"""
Overall Risk Statistics:
- Mean Risk Score: {mean_score:.2f}/5.0
- Standard Deviation: {std_score:.2f}
- Total Risk Assessments: {len(numeric_data)}
"""
    
    return overview

def generate_geographic_analysis(processed_data, statistics):
    """Generate geographic analysis section"""
    
    geo_analysis = """
GEOGRAPHIC ANALYSIS
===================

State-wise Risk Distribution:
"""
    
    state_risks = statistics.get('risk_by_state', {})
    if state_risks:
        # Sort states by risk level
        sorted_states = sorted(state_risks.items(), key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
        
        for i, (state, score) in enumerate(sorted_states[:10], 1):
            if score is not None:
                risk_level = get_risk_level(score)
                geo_analysis += f"{i:2d}. {state}: {score:.2f}/5.0 ({risk_level})\n"
    
    return geo_analysis

def generate_port_type_comparison(statistics):
    """Generate port type comparison analysis"""
    
    comparison = """
PORT TYPE COMPARISON
====================

Risk Levels by Organization Type:
"""
    
    port_risks = statistics.get('risk_by_port_type', {})
    for port_type, categories in port_risks.items():
        if port_type and categories:
            avg_score = np.mean([score for score in categories.values() if score is not None])
            comparison += f"\n{port_type} (Average: {avg_score:.2f}/5.0):\n"
            
            for category, score in categories.items():
                if score is not None:
                    comparison += f"  - {category}: {score:.2f}\n"
    
    return comparison

def generate_time_period_analysis(statistics):
    """Generate time period analysis"""
    
    time_analysis = """
TIME PERIOD ANALYSIS
====================

Risk Evolution Over Time:
"""
    
    period_risks = statistics.get('risk_by_time_period', {})
    for period, categories in period_risks.items():
        if period and categories:
            avg_score = np.mean([score for score in categories.values() if score is not None])
            risk_level = get_risk_level(avg_score)
            time_analysis += f"\n{period} (Average: {avg_score:.2f}/5.0 - {risk_level}):\n"
            
            for category, score in categories.items():
                if score is not None:
                    time_analysis += f"  - {category}: {score:.2f}\n"
    
    return time_analysis

def generate_top_risks_analysis(statistics):
    """Generate top risks analysis"""
    
    top_risks_section = """
TOP RISK ITEMS
==============

Highest Risk Items by Category:
"""
    
    top_risks = statistics.get('top_risks', {})
    for category, risks in top_risks.items():
        if risks:
            top_risks_section += f"\n{category}:\n"
            for i, (risk_desc, score) in enumerate(list(risks.items())[:5], 1):
                if score is not None:
                    risk_level = get_risk_level(score)
                    top_risks_section += f"{i}. {risk_desc}: {score:.2f}/5.0 ({risk_level})\n"
    
    return top_risks_section

def generate_recommendations(statistics):
    """Generate key recommendations"""
    
    recommendations = """
KEY RECOMMENDATIONS
===================

Based on the risk assessment analysis, the following key recommendations are provided:

1. Immediate Priority Areas (2025):
"""
    
    # Identify highest risk categories
    overall_risks = statistics.get('overall_risk_levels', {})
    if overall_risks:
        high_risks = [(cat, score) for cat, score in overall_risks.items() 
                     if score is not None and score >= 3.5]
        high_risks.sort(key=lambda x: x[1], reverse=True)
        
        for category, score in high_risks[:3]:
            recommendations += f"   - {category}: Requires immediate attention and mitigation planning\n"
    
    recommendations += """
2. Medium-term Strategic Planning (2026-2027):
   - Focus on emerging risks identified in the assessment
   - Develop comprehensive risk management frameworks
   - Enhance inter-organizational coordination

3. Long-term Resilience Building (up to 2035):
   - Invest in infrastructure and technology upgrades
   - Develop adaptive capacity for climate and environmental risks
   - Establish continuous monitoring and early warning systems

4. Cross-cutting Recommendations:
   - Enhance data collection and analysis capabilities
   - Strengthen stakeholder engagement and communication
   - Develop standardized risk assessment methodologies
   - Create knowledge sharing platforms across ports

5. Monitoring and Evaluation:
   - Establish key risk indicators (KRIs)
   - Implement regular risk assessment cycles
   - Create dashboards for real-time risk monitoring
   - Develop incident reporting and learning systems
"""
    
    return recommendations

def get_risk_level(score):
    """Determine risk level based on score"""
    if score >= 4.0:
        return "Critical"
    elif score >= 3.0:
        return "High"
    elif score >= 2.0:
        return "Medium"
    elif score >= 1.0:
        return "Low"
    else:
        return "Very Low"

if __name__ == "__main__":
    generate_insights_report()
