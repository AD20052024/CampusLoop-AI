from app.rules.waste_risk import calculate_risk

def test_low_risk():
    result = calculate_risk(5)
    assert result['risk_level'] == 'Low'

def test_medium_risk():
    result = calculate_risk(15)
    assert result['risk_level'] == 'Medium'

def test_high_risk():
    result = calculate_risk(30)
    assert result['risk_level'] == 'High'