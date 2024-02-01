# agent_utils.py

def process_course_info(course_info):
    """
    Procesa la información del curso y genera un texto descriptivo.
    """
    # Extraer los detalles necesarios del curso
    name = course_info['name']
    general_objective = course_info['general_objective']
    module_objective = course_info['module_objective']
    prerequisites = course_info['prerequisites']
    categories = ', '.join([category['name'] for category in course_info['categories']['categories']])
    reference_videos=course_info['reference_videos']
    
    # Crear un texto descriptivo del curso
    course_description = (
        f"Curso: {name}\n"
        f"Objetivo General: {general_objective}\n"
        f"Objetivo del Módulo: {module_objective}\n"
        f"Prerrequisitos: {prerequisites}\n"
        f"Categorías: {categories}"
    )
    
    return course_description,reference_videos


