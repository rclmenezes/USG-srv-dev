import codecs
import os
import sys
import traceback

def parse_time(sem, year):
    """Given a semester and year string, parses and returns them. For
    example: maps ``(S, 2007)`` to 74 and ``(F, 2006)`` to 72 and
    ``(S, 2006)`` to 64 and ``(F, 2006)`` to 62."""

    sem  = sem.upper()
    assert sem in 'FS'

    year = int(year) - 2000
    sem  = dict(F=2, S=4)[sem]
    # Mistake on the part of the registrar? Used to get the Fall 2009
    # information working.
    if sem == 2: year += 1

    return '%03d' % (year * 10 + sem)

def parse_scg_file(semester, year, ending):
    index = parse_time(semester, year)
    file_name = 'TF1' + index + ending + '.txt'

    # Encoding guaranteed by Emacs.
    scg_file = codecs.open(file_name, 'r', 'utf8')
    rows = scg_file.readlines()

    lines = []
    for row in rows:
        lines.append([x.strip(' \r\n"') for x in row.split('\t')])

    headers = {
        'SCG':['dep1','num1','dep2','num2','blank','dr','title','is_cancelled','is_closed','professor1','professor2','professor3','pid1','pid2','pid3','cid'],
        'CT':['dep1','num1','term','blank','dr','author1','author2','author3','author4','author5','author6','dep2','num2','description','title','grade_midterm','grade_paper_for_midterm','grade_final','grade_paper_for_final','grade_other_exam','grade_take_home_midterm','grade_design_projects','grade_take_home_final','grade_programming','grade_quizzes','grade_lab_reports','grade_papers','grade_oral_presentation','grade_term_paper','grade_precept','grade_problem_sets','grade_other','pdf_option','pdf_only','max_enrollment','audit_option','app_or_interview_required','pre_course_preference_required','freshmen_allowed','upperclassmen_only','blank','requirement_group','required_for_concentrators','blank','course_card_initialed_by','other_info','cross_lists','cid'],
        'ST':['dep','num','term','format','format_number','format_sub_section','session','begins','ends','is_tba','day1','day2','day3','day4','day5','section_cancelled','building','room','blank','estimated_enrollment','max_enrollment','is_course_published','is_section_published','blank','blank','blank','blank','blank','blank','blank','blank','blank','blank','blank','blank','blank','blank','is_closed','sid','class_stat','cid'],
        'XL':['dep1','num1','term','offer_number','dr','dep','num','blank','title','cross_list','cid']
    }
    headers['C2'] = headers['CT']
    header = headers[ending]

    data = []
    for line in lines:
        try:
            row = {}
            for i, item in enumerate(line):
                row[header[i]] = item
            data.append(row)
        except Exception, e:
            print 'Invalid formatting from register for %s %s' % (line[0], line[1])
            traceback.print_exc()

    return data
