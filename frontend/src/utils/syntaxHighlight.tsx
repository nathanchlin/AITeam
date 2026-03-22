// Simple syntax highlighting for code blocks
// Supports: JavaScript, TypeScript, Python, JSON, CSS, HTML, Bash

interface Token {
  type: 'keyword' | 'string' | 'number' | 'comment' | 'function' | 'operator' | 'punctuation' | 'plain';
  value: string;
}

// Language keywords
const KEYWORDS: Record<string, Set<string>> = {
  javascript: new Set(['const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'new', 'this', 'class', 'extends', 'import', 'export', 'from', 'default', 'async', 'await', 'try', 'catch', 'finally', 'throw', 'typeof', 'instanceof', 'null', 'undefined', 'true', 'false', 'in', 'of', 'yield', 'static', 'get', 'set', 'super']),
  typescript: new Set(['const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'new', 'this', 'class', 'extends', 'import', 'export', 'from', 'default', 'async', 'await', 'try', 'catch', 'finally', 'throw', 'typeof', 'instanceof', 'null', 'undefined', 'true', 'false', 'in', 'of', 'yield', 'static', 'get', 'set', 'super', 'interface', 'type', 'enum', 'implements', 'private', 'public', 'protected', 'readonly', 'abstract', 'namespace', 'declare', 'as', 'is', 'keyof', 'infer', 'never', 'unknown', 'any', 'void']),
  python: new Set(['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'raise', 'pass', 'break', 'continue', 'lambda', 'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False', 'global', 'nonlocal', 'assert', 'del', 'async', 'await', 'match', 'case']),
  bash: new Set(['if', 'then', 'else', 'elif', 'fi', 'for', 'do', 'done', 'while', 'until', 'case', 'esac', 'function', 'return', 'exit', 'break', 'continue', 'local', 'export', 'readonly', 'declare', 'echo', 'printf', 'read', 'test', 'true', 'false', 'null', 'source', 'alias', 'unalias', 'set', 'unset', 'shift', 'eval', 'exec']),
};

// Token colors
const TOKEN_COLORS: Record<string, string> = {
  keyword: 'text-purple-400',
  string: 'text-green-400',
  number: 'text-orange-400',
  comment: 'text-gray-500 italic',
  function: 'text-yellow-300',
  operator: 'text-red-400',
  punctuation: 'text-gray-400',
  plain: 'text-gray-300',
};

function detectLanguage(lang: string): string {
  const normalized = lang.toLowerCase();
  if (['js', 'javascript', 'node'].includes(normalized)) return 'javascript';
  if (['ts', 'typescript'].includes(normalized)) return 'typescript';
  if (['py', 'python'].includes(normalized)) return 'python';
  if (['sh', 'bash', 'shell', 'zsh'].includes(normalized)) return 'bash';
  if (['json'].includes(normalized)) return 'json';
  if (['css', 'scss'].includes(normalized)) return 'css';
  if (['html', 'htm', 'xml', 'svg'].includes(normalized)) return 'html';
  return normalized;
}

function tokenize(code: string, language: string): Token[] {
  const tokens: Token[] = [];
  const keywords = KEYWORDS[language] || new Set();
  const isJson = language === 'json';

  let i = 0;
  while (i < code.length) {
    // Comments (single line)
    if ((code[i] === '/' && code[i + 1] === '/') || code[i] === '#') {
      let comment = code[i];
      i++;
      if (code[i - 1] === '/') {
        comment += code[i];
        i++;
      }
      while (i < code.length && code[i] !== '\n') {
        comment += code[i];
        i++;
      }
      tokens.push({ type: 'comment', value: comment });
      continue;
    }

    // Multi-line comments
    if (code[i] === '/' && code[i + 1] === '*') {
      let comment = '/*';
      i += 2;
      while (i < code.length && !(code[i] === '*' && code[i + 1] === '/')) {
        comment += code[i];
        i++;
      }
      if (i < code.length) {
        comment += '*/';
        i += 2;
      }
      tokens.push({ type: 'comment', value: comment });
      continue;
    }

    // Strings (double quotes)
    if (code[i] === '"') {
      let str = '"';
      i++;
      while (i < code.length && code[i] !== '"') {
        if (code[i] === '\\' && i + 1 < code.length) {
          str += code[i] + code[i + 1];
          i += 2;
        } else {
          str += code[i];
          i++;
        }
      }
      if (i < code.length) {
        str += '"';
        i++;
      }
      tokens.push({ type: 'string', value: str });
      continue;
    }

    // Strings (single quotes)
    if (code[i] === "'") {
      let str = "'";
      i++;
      while (i < code.length && code[i] !== "'") {
        if (code[i] === '\\' && i + 1 < code.length) {
          str += code[i] + code[i + 1];
          i += 2;
        } else {
          str += code[i];
          i++;
        }
      }
      if (i < code.length) {
        str += "'";
        i++;
      }
      tokens.push({ type: 'string', value: str });
      continue;
    }

    // Template literals
    if (code[i] === '`') {
      let str = '`';
      i++;
      while (i < code.length && code[i] !== '`') {
        if (code[i] === '\\' && i + 1 < code.length) {
          str += code[i] + code[i + 1];
          i += 2;
        } else {
          str += code[i];
          i++;
        }
      }
      if (i < code.length) {
        str += '`';
        i++;
      }
      tokens.push({ type: 'string', value: str });
      continue;
    }

    // Numbers
    if (/\d/.test(code[i]) && (i === 0 || !/\w/.test(code[i - 1]))) {
      let num = '';
      while (i < code.length && /[\d.xXa-fA-F]/.test(code[i])) {
        num += code[i];
        i++;
      }
      tokens.push({ type: 'number', value: num });
      continue;
    }

    // Identifiers and keywords
    if (/[a-zA-Z_]/.test(code[i])) {
      let word = '';
      while (i < code.length && /[\w]/.test(code[i])) {
        word += code[i];
        i++;
      }

      // Check if it's a function call
      let j = i;
      while (j < code.length && /\s/.test(code[j])) j++;
      const isFunction = code[j] === '(';

      if (isJson) {
        // In JSON, property names are strings-like
        if (keywords.has(word)) {
          tokens.push({ type: 'keyword', value: word });
        } else if (isFunction) {
          tokens.push({ type: 'function', value: word });
        } else {
          tokens.push({ type: 'string', value: word });
        }
      } else if (keywords.has(word)) {
        tokens.push({ type: 'keyword', value: word });
      } else if (isFunction) {
        tokens.push({ type: 'function', value: word });
      } else {
        tokens.push({ type: 'plain', value: word });
      }
      continue;
    }

    // Operators
    if (/[+\-*/%=<>!&|^~?:]/.test(code[i])) {
      let op = '';
      while (i < code.length && /[+\-*/%=<>!&|^~?:]/.test(code[i])) {
        op += code[i];
        i++;
      }
      tokens.push({ type: 'operator', value: op });
      continue;
    }

    // Punctuation
    if (/[{}[\]();,.]/.test(code[i])) {
      tokens.push({ type: 'punctuation', value: code[i] });
      i++;
      continue;
    }

    // Whitespace and other
    tokens.push({ type: 'plain', value: code[i] });
    i++;
  }

  return tokens;
}

export function highlightCode(code: string, language: string): React.ReactNode[] {
  const detectedLang = detectLanguage(language);
  const tokens = tokenize(code, detectedLang);
  const result: React.ReactNode[] = [];

  tokens.forEach((token, index) => {
    const colorClass = TOKEN_COLORS[token.type] || TOKEN_COLORS.plain;
    if (token.type === 'plain') {
      result.push(token.value);
    } else {
      result.push(
        <span key={index} className={colorClass}>
          {token.value}
        </span>
      );
    }
  });

  return result;
}

// Parse message content and extract code blocks
export interface ParsedContent {
  type: 'text' | 'code' | 'inline-code';
  content: string;
  language?: string;
}

export function parseCodeBlocks(content: string): ParsedContent[] {
  const parts: ParsedContent[] = [];
  // Match triple backtick code blocks first
  const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    // Add text before code block
    if (match.index > lastIndex) {
      // Process inline code in the text part
      const textBefore = content.substring(lastIndex, match.index);
      parts.push(...parseInlineCode(textBefore));
    }

    // Add code block
    parts.push({
      type: 'code',
      content: match[2].trimEnd(),
      language: match[1] || 'plaintext',
    });

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text with inline code processing
  if (lastIndex < content.length) {
    const remainingText = content.substring(lastIndex);
    parts.push(...parseInlineCode(remainingText));
  }

  return parts.length > 0 ? parts : [{ type: 'text', content }];
}

// Parse inline code (single backticks)
function parseInlineCode(text: string): ParsedContent[] {
  const parts: ParsedContent[] = [];
  const inlineCodeRegex = /`([^`]+)`/g;
  let lastIndex = 0;
  let match;

  while ((match = inlineCodeRegex.exec(text)) !== null) {
    // Add text before inline code
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: text.substring(lastIndex, match.index),
      });
    }

    // Add inline code
    parts.push({
      type: 'inline-code',
      content: match[1],
    });

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push({
      type: 'text',
      content: text.substring(lastIndex),
    });
  }

  return parts.length > 0 ? parts : [{ type: 'text', content: text }];
}
