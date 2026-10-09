from tenacity import retry, wait_exponential, stop_after_attempt
from setup_assets import generate_certificate as draw_certificate

@retry(wait=wait_exponential(multiplier=2, min=2, max=10), stop=stop_after_attempt(3))
def robust_draw_certificate(name, achievement, date, certificate_id, output_path):
    print(f"Drawing certificate for {name} retry attempt {robust_draw_certificate.retry.statistics['attempt_number']}")

    draw_certificate(
        name=name, 
        achievement=achievement, 
        date=date, 
        certificate_id=certificate_id, 
        output_path=output_path
    )
