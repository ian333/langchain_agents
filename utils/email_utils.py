from string import Template
from decouple import config
import smtplib
from email.message import EmailMessage
from email.message import errors

def send_email(to, subject, content):
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = config("username")
        msg['To'] = to

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(config("username"), config("password"))
            server.send_message(msg)
        return "Email sent successfully"
    except Exception as e:
        return f"An error occurred: {e}"







def email_template_user(progress_check, encouragement, wellness_check, learning_tips, milestone_celebration):
    return Template("""
            Dear [Student's Name],

I hope this message finds you well and brimming with curiosity! 🌈 I just wanted to drop a quick, friendly reminder to take a moment and review your progress on this week's fascinating topic: **'X'**. As you delve into these lessons, remember that grasping the nuances of 'X' is a stepping stone to mastering the broader and exciting world of **'Y'**. 📚✨

Why is this important, you might ask? Well, here's the thing:

1. **Deep Understanding:** By fully engaging with 'X', you're not just memorizing facts; you're developing a deep understanding that will be the foundation for future learning. Think of it as planting seeds that will grow into a forest of knowledge. 🌳
2. **Skill Development:** This isn't just about 'X' and 'Y'. It's about honing your skills in critical thinking, problem-solving, and perhaps even creativity. These skills are your toolbox for success in all your future endeavors. 🔧🎨
3. **Confidence Boost:** Each step you take in understanding 'X' builds your confidence. With every topic you master, you're proving to yourself just how capable and brilliant you are. Believe me, that's a superpower in itself! 💪✨
4. **Connecting the Dots:** 'X' might seem like a standalone topic, but it's actually a crucial piece of a larger puzzle. By understanding it, you're preparing yourself to grasp 'Y' and beyond, making connections that many miss. 🧩
5. **Personal Growth:** Every bit of knowledge you acquire contributes to your personal growth. You're not just learning about 'X' and 'Y'; you're growing as a thinker, a learner, and a future leader. 🚀
6. **Joy of Learning:** Remember, learning is not just a path to a goal. It's a journey to be enjoyed. Discover the joy in understanding 'X', and you'll find that your educational journey is as rewarding as it is enlightening. 🌟

So, take a little time today to reflect on what you've learned about 'X'. If you have any questions or need a bit of guidance, don't hesitate to reach out. I'm here to support you on this exciting journey. (link to SkillsAI)

Keep up the great work – your dedication and enthusiasm is truly inspiring! Looking forward to seeing all the amazing things you'll achieve.

Warm regards,

(SkillAI profesor name)







    **Learning Progress Check-In:** $progress_check

    **Encouragement and Motivation:** $encouragement

    **Wellness Check:** $wellness_check

    **Personalized Learning Tips:** $learning_tips

    **Celebrating Milestones:** $milestone_celebration
    """).substitute(progress_check=progress_check, encouragement=encouragement, wellness_check=wellness_check, learning_tips=learning_tips, milestone_celebration=milestone_celebration)

# Similar funciones para los demás tipos de correos...


Learning_process="""Dear [Student's Name],

I hope this message finds you well and brimming with curiosity! 🌈 I just wanted to drop a quick, friendly reminder to take a moment and review your progress on this week's fascinating topic: **'X'**. As you delve into these lessons, remember that grasping the nuances of 'X' is a stepping stone to mastering the broader and exciting world of **'Y'**. 📚✨

Why is this important, you might ask? Well, here's the thing:

1. **Deep Understanding:** By fully engaging with 'X', you're not just memorizing facts; you're developing a deep understanding that will be the foundation for future learning. Think of it as planting seeds that will grow into a forest of knowledge. 🌳
2. **Skill Development:** This isn't just about 'X' and 'Y'. It's about honing your skills in critical thinking, problem-solving, and perhaps even creativity. These skills are your toolbox for success in all your future endeavors. 🔧🎨
3. **Confidence Boost:** Each step you take in understanding 'X' builds your confidence. With every topic you master, you're proving to yourself just how capable and brilliant you are. Believe me, that's a superpower in itself! 💪✨
4. **Connecting the Dots:** 'X' might seem like a standalone topic, but it's actually a crucial piece of a larger puzzle. By understanding it, you're preparing yourself to grasp 'Y' and beyond, making connections that many miss. 🧩
5. **Personal Growth:** Every bit of knowledge you acquire contributes to your personal growth. You're not just learning about 'X' and 'Y'; you're growing as a thinker, a learner, and a future leader. 🚀
6. **Joy of Learning:** Remember, learning is not just a path to a goal. It's a journey to be enjoyed. Discover the joy in understanding 'X', and you'll find that your educational journey is as rewarding as it is enlightening. 🌟

So, take a little time today to reflect on what you've learned about 'X'. If you have any questions or need a bit of guidance, don't hesitate to reach out. I'm here to support you on this exciting journey. (link to SkillsAI)

Keep up the great work – your dedication and enthusiasm is truly inspiring! Looking forward to seeing all the amazing things you'll achieve.

Warm regards,

(SkillAI profesor name)"""
