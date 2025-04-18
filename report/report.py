from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_file_data(folder_name, filenames):
    return [
        {
            'filename': fname,
            'path': os.path.join('..', folder_name, fname)
        }
        for fname in filenames
    ]

def render_template(template_name, context, template_folder):
    env = Environment(loader=FileSystemLoader(template_folder))
    template = env.get_template(template_name)
    return template.render(context)

def save_report(output_html, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(output_html)
        
def main():
    project_root = get_project_root()
    template_folder = os.path.join(project_root, 'templates')
    data_path = 'data/plots'
    model_path = 'model/results'
    
    def build_plot(folder, filename):
        return {
            'filename': filename,
            'path': os.path.join('..', folder, filename)
        }

    context = {
        'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        
        # Plots
        'plot_summary': build_plot(data_path, 'summary_stats.png'),
        'plot_defaults': build_plot(data_path, 'defaults_per_month.png'),
        'plot_delinquency_status': build_plot(data_path, 'delinquency_status_trends_linechart.png'),
        'plot_current_status': build_plot(data_path, 'current_status_trend_linechart.png'),
        'plot_loan_age': build_plot(data_path, 'loan_age_by_default.png'),
        'plot_credit_score': build_plot(data_path, 'credit_score_by_default.png'),
        'plot_interest_rate': build_plot(data_path, 'interest_rate_by_default.png'),
        'plot_orig_cltv': build_plot(data_path, 'original_cltv_by_default.png'),
        'plot_orig_dti': build_plot(data_path, 'original_dti_by_default.png'),
        'plot_correlation': build_plot(data_path, 'correlation.png'),

        # Models
        'plot_trace': build_plot(model_path, 'trace_plot.png'),
        'plot_posterior_coefficients': build_plot(model_path, 'posterior_coefficients.png'),
        'plot_posterior_summary': build_plot(model_path, 'posterior_summary.png'),
        'plot_roc_auc': build_plot(model_path, 'roc_curve.png'),
    }

    rendered_html = render_template('report.html.j2', context, template_folder)
    output_file = os.path.join('report', 'report.html')
    save_report(rendered_html, output_file)

    print("Report generated successfully:", output_file)


if __name__ == '__main__':
    main()
