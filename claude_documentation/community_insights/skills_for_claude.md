# Skills for Claude!

**Source:** https://blog.fsck.com/2025/10/16/skills-for-claude/  
**Author:** Jesse Vincent (obra)  
**Tags:** ai, writing, strunk

Anthropic is releasing their first-party Skills system across Claude Code, Claude.ai and the Claude API, all launching today. I can tell that they've been working on it for quite a while and I'm really excited about it.

In just a few minutes, I plan to release a new version of Superpowers that uses the official Skills system. Shortly after I first published this blog post, I released a new version of Superpowers that uses the official Skills system.

One of the new skills they were gracious enough to allow me to test out is a new 'creating MCPs' skill. Other than a small issue with the tool descriptions it generates being too verbose, it was by far the smoothest MCP development experience I've had so far. (I used it to make the 'search' tool for a new episodic memory plugin I'm building for Claude Code that I hope to release soon.)

I've been using skills in Claude Code for the better part of a month. Last week, when Anthropic shipped plugins support for Claude code, I celebrated by releasing my homebrew skills system as Superpowers for Claude Code.

Superpowers is a couple of things:

A bootstrap that teaches Claude Code to load SKILL.md files and when to use them, built as a SKILL.md file, a search tool, and a hook that initializes things on startup.
A set of SKILL.md files designed to create, manage, and share SKILL.md files.
A set of SKILL.md files that encode my Architect/Implementer agentic coding methodolgy, starting from the brainstorming process and running all the way through the TDD process.
A set of SKILL.md files that encode a bunch of other software engineering skills.
Over the weekend, while I was reviewing a bug report from an end user, I saw a bunch of logging output from claude --debug that talked about skill files and skills directories. Which would make sense, since I was debugging a skills system.

The only problem was that the logging wasn't from Superpowers. (As a slightly funny aside: I had to check whether the log messages were from Superpowers or not. Since Claude did all the actual implementation work for Superpowers, I'd never actually looked at that bit of code.)

I built out Superpowers' core skill system based on spelunking around in Anthropic's initial few MS Office skills and bolting together some bits and pieces, along with some weird ideas I wanted to try out.

At the time, I had no idea that Claude Code had an apparently-complete implementation of a skills system hidden inside. Based on Anthropic's documentation, the first-party skills system has some support in Claude Code 2.0.0 and may have been there as far back as Claude Code 1.0!?

Had I known that Claude Code already had the magic bootstrappy parts that make SKILL.md files useful if their metadata is put together in just the right way, I absolutely wouldn't have built my own.

But, now that Skills are officially a thing, Superpowers is embracing the future.

As I'm starting to get familiar with the official skills system, it looks like the biggest design difference is that Anthropic's skills have a name, a description, a license (I think?) and a metadata field. Our skills had...flexible frontmatter, but the important parts were name, description, and when_to_use – We broke apart the answers to "When should Claude use this skill?" and "What does this skill do?" I still think that that distinction is important. In my testing, I've found that showing only "When should Claude use this skill?" leads to better compliance. When Claude thinks it knows what a skill does, it's more likely to believe it's using the skill and just wing it, even if it hasn't read it yet.

I've rewritten our core skills to switch things over to Anthropic's way of doing things. I've also broken apart our core skills into core Superpowers skills and a set of skills that we learned from Microsoft's Amplifier.

I haven't had as much time to play around with Anthropic's skills as I'd like, and most of what I've seen has been on Claude.ai.

As I've been exploring, the part of all this that's most interesting to me is getting the LLM to create its own skills. Making that work well is the key to a whole bunch of avenues for agentic self-improvement.

As far as I can tell, Anthropic's skill creation methodology is pretty different than mine. Rather than poke inside Anthropic's skill creation metaskill, I did what any good engineer would do in 2025: I uploaded my writing-skills/SKILL.md to Claude.ai, asked it to compare and contrast it with Anthropic's first-party skill-creation metaskill, and went to grab a cup of coffee.

I came back to a pretty detailed report comparing and contrasting the two approaches. Their skill has a lot more detail on the details of generating the skill and includes templates to copy. Mine spends a lot more time on testing the skill, looking for ways to avoid Claude's rationalizations about why it shouldn't need to use the skill, and persuasion techniques that can help ensure compliance.

skillglazing

Unsurprisingly, Claude is a fan of TDD.

In Claude Code, Skills are SKILL.md files included in directories inside ~/.claude/skills/, in .claude/skills in a project directory, and in the skills subdirectory of plugins.

Right now, it looks like Skills are being executed as /commands with a new Skill tool.

Skills are themselves able to execute /commands tools that don't have a frontmatter flag that disables command execution.

Skills can also be included in the skills/ directory of any plugin.

One thing about all of this that I find really funny is that that is exactly where I'd put Superpowers' skills, before I moved them out into another git repository to make it easier for users to customize them and share their improvements.

Claude code automatically indexes all skills into the system prompt. I'm hoping that they eventually allow us to hide some skills from immediate disclosure, to let us build more complicated "composite" skills, like a 'debugging' skill that can link through to additional skills.

I spent some time over the past couple days getting our skills ready for this brave new world, but they're not quite ready yet. The new system (hopefully) gets rid of the session startup hook, separate git repo for skills and find-skills tool. Now that skills can be managed like subagent personae or /commands, Superpowers doesn't need to build its own plugin system or become a giant monorepo of skills.

Skills are incredibly powerful. They're magic words that make your agent behave differently, even without you asking directly. They can bundle scripts and binaries (which should still be subject to your regular tool use authorizations, I believe.) They're not just subject to prompt injection–They are the very definition of prompt injection. (Despite the emdash and the "It's not X, it's Y" formation, that sentence was 100% human authored, albeit quite late at night.)

I'm still working through issues convincing Claude to always execute the brainstorming skill automatically when it detects that the user wants to create or code something.

Claude Code knows it's supposed to use skills automatically, but it's not relaible for me just yet. At least temporarily, I've adapted my 'using-skills' skill into a new 'using-superpowers' skill and updated Superpowers' session start hook to load when Claude Code starts up. As I get familiar with the new system, I'm hopeful that I'll be able to remove that shim.

Even when we don't need it for Claude Code anymore, the using-superpowers/SKILL.md should work just great with gemini-cli and codex. Once it does, the whole new world of SKILL.md skills should be open to them, too.

I'm hoping to find time to work on skills for those other platforms, but I'd be grateful if you (yes, you) wanted to beat me to it and contribute those features back to Superpowers.