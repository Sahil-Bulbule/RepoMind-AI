import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ResponseSection from './ResponseSection';
import CodeBlock from './CodeBlock';
import TechnologyBadge from './TechnologyBadge';
import FeatureCard from './FeatureCard';
import FileStructureCard from './FileStructureCard';
import WarningCard from './WarningCard';
import TipCard from './TipCard';
import StepCard from './StepCard';
import SummaryCard from './SummaryCard';
import InfoCard from './InfoCard';
import { 
  Box, 
  Cpu, 
  Layers, 
  Terminal, 
  FileCode, 
  GitBranch, 
  AlertTriangle, 
  Lightbulb, 
  Zap, 
  Database,
  Bot
} from 'lucide-react';

const COMMON_TECHS = [
  'python', 'react', 'fastapi', 'typescript', 'javascript', 'docker',
  'chromadb', 'pytorch', 'tensorflow', 'tailwind', 'nextjs',
  'nodejs', 'postgresql', 'mongodb', 'langchain', 'redis', 'flask',
  'django', 'sqlite', 'vue', 'angular', 'pandas', 'numpy', 'scikit-learn'
];

   
                                              
   
function classifySection(heading = '') {
  const h = heading.toLowerCase();

  if (h.includes('overview') || h.includes('summary') || h.includes('introduction') || h.includes('about')) {
    return { type: 'overview', title: heading, emoji: '📦', icon: Box, badge: 'Overview', badgeVariant: 'rose' };
  }
  if (h.includes('what it does') || h.includes('purpose') || h.includes('goal') || h.includes('mission')) {
    return { type: 'purpose', title: heading, emoji: '🧠', icon: Cpu, badge: 'Functionality', badgeVariant: 'crimson' };
  }
  if (h.includes('technolog') || h.includes('tech stack') || h.includes('tools') || h.includes('dependencies') || h.includes('framework')) {
    return { type: 'technologies', title: heading, emoji: '⚙️', icon: Terminal, badge: 'Tech Stack', badgeVariant: 'slate' };
  }
  if (h.includes('structure') || h.includes('file') || h.includes('directory') || h.includes('codebase layout')) {
    return { type: 'structure', title: heading, emoji: '📁', icon: FileCode, badge: 'Architecture', badgeVariant: 'rose' };
  }
  if (h.includes('feature') || h.includes('capability') || h.includes('capabilities') || h.includes('highlights')) {
    return { type: 'features', title: heading, emoji: '🚀', icon: Zap, badge: 'Key Capabilities', badgeVariant: 'crimson' };
  }
  if (h.includes('architecture') || h.includes('data flow') || h.includes('system design') || h.includes('workflow')) {
    return { type: 'architecture', title: heading, emoji: '🏗️', icon: Layers, badge: 'System Design', badgeVariant: 'slate' };
  }
  if (h.includes('ai') || h.includes('ml') || h.includes('rag') || h.includes('model') || h.includes('embedding')) {
    return { type: 'aiml', title: heading, emoji: '🤖', icon: Bot, badge: 'AI Engine', badgeVariant: 'rose' };
  }
  if (h.includes('install') || h.includes('getting started') || h.includes('setup') || h.includes('run') || h.includes('usage') || h.includes('how to use')) {
    return { type: 'installation', title: heading, emoji: '💻', icon: Terminal, badge: 'Guide', badgeVariant: 'emerald' };
  }
  if (h.includes('warning') || h.includes('caveat') || h.includes('limitation') || h.includes('observation') || h.includes('important note')) {
    return { type: 'warning', title: heading, emoji: '⚠️', icon: AlertTriangle, badge: 'Notice', badgeVariant: 'crimson' };
  }
  if (h.includes('tip') || h.includes('recommend') || h.includes('best practice')) {
    return { type: 'tip', title: heading, emoji: '💡', icon: Lightbulb, badge: 'Recommendation', badgeVariant: 'rose' };
  }

  return { type: 'general', title: heading, emoji: '📌', icon: Layers, badge: null, badgeVariant: 'slate' };
}

   
                                     
   
function extractTechnologies(text = '') {
  const found = new Set();
  const lower = text.toLowerCase();
  
  COMMON_TECHS.forEach((tech) => {
                              
    const regex = new RegExp(`\\b${tech}\\b`, 'i');
    if (regex.test(lower)) {
      found.add(tech);
    }
  });

                                                                                   
  const match = text.match(/(?:technologies|tech stack|built with|frameworks):\s*([^\n]+)/i);
  if (match && match[1]) {
    const rawList = match[1].split(/[,·•|]/);
    rawList.forEach((item) => {
      const trimmed = item.replace(/[`*]/g, '').trim();
      if (trimmed.length > 1 && trimmed.length < 30) {
        found.add(trimmed);
      }
    });
  }

  return Array.from(found);
}

   
                                                                        
   
function extractFiles(text = '') {
  const lines = text.split('\n');
  const files = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed.startsWith('-') && !trimmed.startsWith('*')) continue;

                                                                          
    const fileMatch = trimmed.match(/^[-*]\s*(?:[`*]+([^`*:]+)[`*]+|([a-zA-Z0-9_.-]+\/[a-zA-Z0-9_./-]+))\s*[:–-]?\s*(.*)$/);
    if (fileMatch) {
      const path = (fileMatch[1] || fileMatch[2] || '').trim();
      const desc = (fileMatch[3] || '').trim();
      if (path && (path.includes('/') || path.includes('.'))) {
        files.push({ path, description: desc });
      }
    }
  }

  return files;
}

   
                                    
   
function extractFeatures(text = '') {
  const lines = text.split('\n');
  const features = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
      const raw = trimmed.replace(/^[-*]\s*/, '').trim();
                                                                  
      const boldMatch = raw.match(/^\*\*([^*]+)\*\*[:–-]?\s*(.*)$/);
      if (boldMatch) {
        features.push({ title: boldMatch[1].trim(), description: boldMatch[2].trim() });
      } else if (raw.length > 5) {
                                   
        const parts = raw.split(/[:–-]/);
        if (parts.length > 1) {
          features.push({ title: parts[0].trim(), description: parts.slice(1).join(' - ').trim() });
        } else {
          features.push({ title: raw, description: '' });
        }
      }
    }
  }

  return features;
}

   
                         
   
function extractSteps(text = '') {
  const lines = text.split('\n');
  const steps = [];
  let currentStep = null;

  for (const line of lines) {
    const stepMatch = line.match(/^(\d+)\.\s+(.*)$/);
    if (stepMatch) {
      if (currentStep) steps.push(currentStep);
      const fullText = stepMatch[2].trim();
      const boldMatch = fullText.match(/^\*\*([^*]+)\*\*[:–-]?\s*(.*)$/);
      if (boldMatch) {
        currentStep = {
          number: parseInt(stepMatch[1], 10),
          title: boldMatch[1].trim(),
          content: boldMatch[2].trim()
        };
      } else {
        currentStep = {
          number: parseInt(stepMatch[1], 10),
          title: fullText,
          content: ''
        };
      }
    } else if (currentStep && line.trim()) {
      currentStep.content += (currentStep.content ? '\n' : '') + line.trim();
    }
  }

  if (currentStep) steps.push(currentStep);
  return steps;
}

   
                                                 
   
function RenderSectionBody({ type, content }) {
                                                                     
  if (type === 'technologies') {
    const techs = extractTechnologies(content);
    if (techs.length > 0) {
      return (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2 pt-1">
            {techs.map((tech, idx) => (
              <TechnologyBadge key={idx} name={tech} />
            ))}
          </div>
                                                             
          <div className="prose-custom text-xs text-slate-300">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                  ) : (
                    <code className={className} {...props}>{children}</code>
                  );
                }
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </div>
      );
    }
  }

                                                            
  if (type === 'structure') {
    const files = extractFiles(content);
    if (files.length >= 2) {
      return (
        <div className="space-y-3">
          <FileStructureCard items={files} />
                                        
          <div className="prose-custom text-xs text-slate-300">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                  ) : (
                    <code className={className} {...props}>{children}</code>
                  );
                }
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </div>
      );
    }
  }

                                                                           
  if (type === 'features') {
    const feats = extractFeatures(content);
    if (feats.length >= 2) {
      return (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {feats.map((feat, idx) => (
              <FeatureCard
                key={idx}
                title={feat.title}
                description={feat.description}
              />
            ))}
          </div>
        </div>
      );
    }
  }

                                                                
  if (type === 'installation') {
    const steps = extractSteps(content);
    if (steps.length >= 2) {
      return (
        <div className="space-y-2">
          {steps.map((st, idx) => (
            <StepCard key={idx} number={st.number} title={st.title}>
              <div className="prose-custom text-xs">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return match ? (
                        <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                      ) : (
                        <code className={className} {...props}>{children}</code>
                      );
                    }
                  }}
                >
                  {st.content}
                </ReactMarkdown>
              </div>
            </StepCard>
          ))}
        </div>
      );
    }
  }

                                                
  return (
    <div className="prose-custom text-sm">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return match ? (
              <CodeBlock
                language={match[1]}
                value={String(children).replace(/\n$/, '')}
              />
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export default function SmartResponseRenderer({ content = '' }) {
  if (!content) return null;

                                                                                        
  const headingRegex = /(?:^|\n)(#{1,4}\s+[^\n]+)/g;
  const parts = content.split(headingRegex);

                                                                                        
  if (parts.length <= 1) {
                                                 
    const isWarning = /^(?:warning|caution|important|alert):/i.test(content.trim());
    if (isWarning) {
      return <WarningCard>{content}</WarningCard>;
    }

    return (
      <SummaryCard title="Answer">
        <div className="prose-custom text-sm">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return match ? (
                  <CodeBlock
                    language={match[1]}
                    value={String(children).replace(/\n$/, '')}
                  />
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      </SummaryCard>
    );
  }

                       
  const sections = [];
  let introText = parts[0]?.trim() || '';

  for (let i = 1; i < parts.length; i += 2) {
    const rawHeading = parts[i] || '';
    const headingClean = rawHeading.replace(/^#+\s*/, '').trim();
    const sectionBody = parts[i + 1]?.trim() || '';

    if (headingClean) {
      const meta = classifySection(headingClean);
      sections.push({
        ...meta,
        rawHeading,
        content: sectionBody,
        rawText: `${rawHeading}\n\n${sectionBody}`,
      });
    }
  }

  return (
    <div className="space-y-4">
                                                            
      {introText && (
        <SummaryCard title="Overview Brief">
          <div className="prose-custom text-sm">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                  ) : (
                    <code className={className} {...props}>{children}</code>
                  );
                }
              }}
            >
              {introText}
            </ReactMarkdown>
          </div>
        </SummaryCard>
      )}

                                     
      {sections.map((section, idx) => (
        <ResponseSection
          key={idx}
          title={section.title}
          emoji={section.emoji}
          icon={section.icon}
          badge={section.badge}
          badgeVariant={section.badgeVariant}
          rawText={section.rawText}
          defaultExpanded={true}
          collapsible={false}
        >
          <RenderSectionBody type={section.type} content={section.content} />
        </ResponseSection>
      ))}
    </div>
  );
}
