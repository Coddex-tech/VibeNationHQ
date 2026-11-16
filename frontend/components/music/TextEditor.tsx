'use client';

import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type ChangeEvent,
  type CompositionEvent,
  type CSSProperties,
  type KeyboardEvent,
  type ReactNode,
  type SyntheticEvent,
} from 'react';

import { createPortal } from 'react-dom';

import VerificationBadge from '../Icons';

export type MentionUser = {
  id: string | number;
  username: string;
  display_name?: string | null;
  is_verified: boolean;
  is_identity_verified?: boolean;
};

type MentionContext = {
  start: number;
  end: number;
  query: string;
};

type MentionToken = {
  start: number;
  end: number;
};

type PendingCaret = {
  position: number;
  value: string;
};

type DropdownPosition = {
  left: number;
  top: number;
  width: number;
  maxHeight: number;
  placement: 'above' | 'below';
};

type TextEditorProps = {
  value: string;
  onChange: (value: string) => void;
  loadSuggestions: (query: string) => Promise<MentionUser[]>;

  placeholder?: string;
  rows?: number;
  maxLength?: number;
  disabled?: boolean;

  autoResize?: boolean;
  minRows?: number;
  maxRows?: number;

  focusRequestKey?: number;

  className?: string;
  containerClassName?: string;

  onEditorKeyDown?: (
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) => void;

  onCompositionStart?: (
    event: CompositionEvent<HTMLTextAreaElement>,
  ) => void;

  onCompositionEnd?: (
    event: CompositionEvent<HTMLTextAreaElement>,
  ) => void;

  onFocus?: () => void;
  onBlur?: () => void;
};

const MAX_SUGGESTIONS = 5;
const SUGGESTION_DELAY = 180;
const DROPDOWN_MAX_HEIGHT = 320;
const DROPDOWN_GAP = 8;
const VIEWPORT_PADDING = 8;

const DEFAULT_TEXTAREA_CLASS =
  'block w-full resize-none rounded-xl border border-light-border bg-transparent px-4 py-3 text-sm leading-6 caret-slate-900 outline-none placeholder:text-light-text-muted focus:border-brand-teal focus:ring-0 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:caret-slate-100 dark:placeholder:text-dark-text-muted';

function getMentionTokenAtPosition(
  text: string,
  cursorPosition: number,
): MentionToken | null {
  const mentionPattern =
    /(^|[^A-Za-z0-9_])@[A-Za-z0-9_.-]+/g;

  let match: RegExpExecArray | null;

  while (
    (match = mentionPattern.exec(text)) !== null
  ) {
    const prefix = match[1];

    const start =
      match.index + prefix.length;

    const end =
      match.index + match[0].length;

    if (
      cursorPosition > start &&
      cursorPosition < end
    ) {
      return { start, end };
    }
  }

  return null;
}

/**
 * Only activates autocomplete when the cursor is at the
 * end of an @query, or immediately after a newly typed @.
 *
 * Moving the cursor inside a username or before an @
 * cannot activate autocomplete.
 */
function getMentionContext(
  text: string,
  cursorPosition: number,
): MentionContext | null {
  if (
    cursorPosition < 0 ||
    cursorPosition > text.length
  ) {
    return null;
  }

  const atIndex = text.lastIndexOf(
    '@',
    cursorPosition - 1,
  );

  if (atIndex === -1) {
    return null;
  }

  const previousCharacter =
    atIndex > 0 ? text[atIndex - 1] : '';

  if (
    previousCharacter &&
    /[A-Za-z0-9_.-]/.test(previousCharacter)
  ) {
    return null;
  }

  const query = text.slice(
    atIndex + 1,
    cursorPosition,
  );

  if (!/^[A-Za-z0-9_.-]*$/.test(query)) {
    return null;
  }

  let end = atIndex + 1;

  while (
    end < text.length &&
    /[A-Za-z0-9_.-]/.test(text[end])
  ) {
    end += 1;
  }

  // The cursor must be at the end of the username.
  // This prevents requests when moving through a username.
  if (cursorPosition !== end) {
    return null;
  }

  // A mention followed by whitespace is already completed.
  // Do not reopen autocomplete when the cursor is placed
  // immediately before that whitespace.
  if (
    end < text.length &&
    /\s/.test(text[end])
  ) {
    return null;
  }

  return {
    start: atIndex,
    end,
    query,
  };
}

/**
 * Highlights syntactically valid mention tokens.
 *
 * The backend remains responsible for validating usernames.
 */
function renderHighlightedText(
  text: string,
): ReactNode[] {
  const mentionPattern =
    /(^|[^A-Za-z0-9_])(@[A-Za-z0-9_.-]+)/g;

  const elements: ReactNode[] = [];

  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while (
    (match = mentionPattern.exec(text)) !== null
  ) {
    const prefix = match[1];
    const mention = match[2];

    const matchStart = match.index;

    const mentionStart =
      matchStart + prefix.length;

    const mentionEnd =
      matchStart + match[0].length;

    if (matchStart > lastIndex) {
      elements.push(
        <span key={`text-${lastIndex}`}>
          {text.slice(lastIndex, matchStart)}
        </span>,
      );
    }

    if (prefix) {
      elements.push(
        <span key={`prefix-${matchStart}`}>
          {prefix}
        </span>,
      );
    }

    elements.push(
      <span
        key={`mention-${mentionStart}`}
        className="font-semibold text-teal-600 dark:text-teal-400"
      >
        {mention}
      </span>,
    );

    lastIndex = mentionEnd;
  }

  if (lastIndex < text.length) {
    elements.push(
      <span key={`text-${lastIndex}`}>
        {text.slice(lastIndex)}
      </span>,
    );
  }

  return elements;
}

export default function TextEditor({
  value,
  onChange,
  loadSuggestions,
  placeholder = 'Write something...',
  rows = 5,
  maxLength,
  disabled = false,
  autoResize = false,
  minRows = 1,
  maxRows = 3,
  focusRequestKey = 0,
  className = '',
  containerClassName = '',
  onEditorKeyDown,
  onCompositionStart,
  onCompositionEnd,
  onFocus,
  onBlur,
}: TextEditorProps) {
  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  const highlightRef =
    useRef<HTMLDivElement>(null);

  const requestVersionRef = useRef(0);

  const pendingCaretRef =
    useRef<PendingCaret | null>(null);

  const isComposingRef = useRef(false);

  /**
   * Prevents autocomplete from reopening while the user
   * is deleting characters from an existing mention.
   */
  const suppressAutocompleteRef = useRef(false);

  const [mentionContext, setMentionContext] =
    useState<MentionContext | null>(null);

  const [suggestions, setSuggestions] =
    useState<MentionUser[]>([]);

  const [activeSuggestionIndex, setActiveSuggestionIndex] =
    useState(0);

  const [isLoading, setIsLoading] =
    useState(false);

  const [suggestionsVisible, setSuggestionsVisible] =
    useState(false);

  const [hasSelection, setHasSelection] =
    useState(false);

  const [dropdownPosition, setDropdownPosition] =
    useState<DropdownPosition | null>(null);

  const closeSuggestions = useCallback(() => {
    setMentionContext(null);
    setSuggestions([]);
    setSuggestionsVisible(false);
    setActiveSuggestionIndex(0);
    setIsLoading(false);
  }, []);

  const updateMentionContext = useCallback(
    (text: string, cursorPosition: number) => {
      if (suppressAutocompleteRef.current) {
        closeSuggestions();
        return;
      }

      const context = getMentionContext(
        text,
        cursorPosition,
      );

      setMentionContext(context);
      setActiveSuggestionIndex(0);
      setSuggestionsVisible(context !== null);

      if (!context) {
        setSuggestions([]);
      }
    },
    [closeSuggestions],
  );

  /**
   * Fetch mention suggestions.
   *
   * Empty query: recently mentioned users.
   * Non-empty query: matching followers and following.
   */
  useEffect(() => {
    if (
      !suggestionsVisible ||
      !mentionContext ||
      disabled
    ) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    let isCurrentRequest = true;

    const requestVersion =
      ++requestVersionRef.current;

    setIsLoading(true);

    const timeout = window.setTimeout(
      async () => {
        try {
          const results = await loadSuggestions(
            mentionContext.query,
          );

          if (
            !isCurrentRequest ||
            requestVersion !== requestVersionRef.current
          ) {
            return;
          }

          setSuggestions(
            Array.isArray(results)
              ? results.slice(0, MAX_SUGGESTIONS)
              : [],
          );

          setActiveSuggestionIndex(0);
        } catch {
          if (
            isCurrentRequest &&
            requestVersion === requestVersionRef.current
          ) {
            setSuggestions([]);
          }
        } finally {
          if (
            isCurrentRequest &&
            requestVersion === requestVersionRef.current
          ) {
            setIsLoading(false);
          }
        }
      },
      SUGGESTION_DELAY,
    );

    return () => {
      isCurrentRequest = false;
      window.clearTimeout(timeout);
    };
  }, [
    disabled,
    loadSuggestions,
    mentionContext,
    suggestionsVisible,
  ]);

  /**
   * Restore the caret after a mention has been inserted.
   *
   * Runs after every committed render so restoration does not
   * depend exclusively on the value prop changing.
   */
  useLayoutEffect(() => {
    const pendingCaret = pendingCaretRef.current;
    const textarea = textareaRef.current;

    if (!pendingCaret || !textarea) {
      return;
    }

    // Wait until React has applied the controlled textarea value.
    if (textarea.value !== pendingCaret.value) {
      return;
    }

    const cursorPosition = Math.min(
      pendingCaret.position,
      textarea.value.length,
    );

    textarea.focus({ preventScroll: true });

    textarea.setSelectionRange(
      cursorPosition,
      cursorPosition,
    );

    pendingCaretRef.current = null;
    setHasSelection(false);

    const highlight = highlightRef.current;

    if (highlight) {
      highlight.scrollTop = textarea.scrollTop;
      highlight.scrollLeft = textarea.scrollLeft;
    }
  });

  /**
   * Automatically focus the editor when requested.
   */
  useEffect(() => {
    if (focusRequestKey <= 0 || disabled) {
      return;
    }

    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.focus({ preventScroll: true });

    const cursorPosition = textarea.value.length;

    textarea.setSelectionRange(
      cursorPosition,
      cursorPosition,
    );
  }, [focusRequestKey, disabled]);

  /**
   * Automatically resize the textarea.
   */
  useEffect(() => {
    if (!autoResize) {
      return;
    }

    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    const computedStyle =
      window.getComputedStyle(textarea);

    const lineHeight =
      Number.parseFloat(computedStyle.lineHeight) || 24;

    const paddingTop =
      Number.parseFloat(computedStyle.paddingTop) || 0;

    const paddingBottom =
      Number.parseFloat(computedStyle.paddingBottom) || 0;

    const borderTop =
      Number.parseFloat(computedStyle.borderTopWidth) || 0;

    const borderBottom =
      Number.parseFloat(computedStyle.borderBottomWidth) || 0;

    const verticalExtras =
      paddingTop +
      paddingBottom +
      borderTop +
      borderBottom;

    const minimumHeight =
      lineHeight * minRows + verticalExtras;

    const maximumHeight =
      lineHeight * maxRows + verticalExtras;

    textarea.style.height = 'auto';

    const nextHeight = Math.min(
      Math.max(
        textarea.scrollHeight,
        minimumHeight,
      ),
      maximumHeight,
    );

    textarea.style.height = `${nextHeight}px`;

    textarea.style.overflowY =
      textarea.scrollHeight > maximumHeight
        ? 'auto'
        : 'hidden';
  }, [
    autoResize,
    maxRows,
    minRows,
    value,
  ]);

  /**
   * Position the dropdown relative to the textarea.
   *
   * The dropdown uses a portal and fixed positioning, so
   * overflow-hidden ancestors cannot crop it.
   */
  useLayoutEffect(() => {
    if (!suggestionsVisible || disabled) {
      setDropdownPosition(null);
      return;
    }

    const updatePosition = () => {
      const textarea = textareaRef.current;

      if (!textarea) {
        return;
      }

      const rect = textarea.getBoundingClientRect();

      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      const width = Math.max(
        0,
        Math.min(
          rect.width,
          384,
          viewportWidth - VIEWPORT_PADDING * 2,
        ),
      );

      const left = Math.max(
        VIEWPORT_PADDING,
        Math.min(
          rect.left,
          viewportWidth - width - VIEWPORT_PADDING,
        ),
      );

      const availableAbove = Math.max(
        0,
        rect.top - DROPDOWN_GAP - VIEWPORT_PADDING,
      );

      const availableBelow = Math.max(
        0,
        viewportHeight -
          rect.bottom -
          DROPDOWN_GAP -
          VIEWPORT_PADDING,
      );

      const placement =
        availableBelow >= DROPDOWN_MAX_HEIGHT ||
        availableBelow >= availableAbove
          ? 'below'
          : 'above';

      const availableHeight =
        placement === 'below'
          ? availableBelow
          : availableAbove;

      const maxHeight = Math.min(
        DROPDOWN_MAX_HEIGHT,
        availableHeight,
      );

      const top =
        placement === 'below'
          ? rect.bottom + DROPDOWN_GAP
          : rect.top - DROPDOWN_GAP;

      setDropdownPosition({
        left,
        top,
        width,
        maxHeight,
        placement,
      });
    };

    updatePosition();

    window.addEventListener(
      'resize',
      updatePosition,
    );

    window.addEventListener(
      'scroll',
      updatePosition,
      true,
    );

    return () => {
      window.removeEventListener(
        'resize',
        updatePosition,
      );

      window.removeEventListener(
        'scroll',
        updatePosition,
        true,
      );
    };
  }, [
    suggestionsVisible,
    disabled,
    isLoading,
    suggestions.length,
  ]);

  const handleChange = (
    event: ChangeEvent<HTMLTextAreaElement>,
  ) => {
    const nextValue = event.target.value;

    const cursorPosition =
      event.target.selectionStart;

    pendingCaretRef.current = null;
    setHasSelection(false);

    onChange(nextValue);

    updateMentionContext(
      nextValue,
      cursorPosition,
    );
  };

  /**
   * Keep the caret outside an existing mention token.
   *
   * A mouse click or selection movement into the middle
   * of a username snaps to the nearest token boundary.
   */
  const handleCursorChange = (
    event: SyntheticEvent<HTMLTextAreaElement>,
  ) => {
    const textarea = event.currentTarget;

    const selectionStart = textarea.selectionStart;
    const selectionEnd = textarea.selectionEnd;

    if (selectionStart !== selectionEnd) {
      setHasSelection(true);
      closeSuggestions();
      return;
    }

    setHasSelection(false);

    if (suppressAutocompleteRef.current) {
      closeSuggestions();
      return;
    }

    const token = getMentionTokenAtPosition(
      textarea.value,
      selectionStart,
    );

    if (token) {
      const distanceToStart =
        selectionStart - token.start;

      const distanceToEnd =
        token.end - selectionStart;

      const nextPosition =
        distanceToStart < distanceToEnd
          ? token.start
          : token.end;

      textarea.setSelectionRange(
        nextPosition,
        nextPosition,
      );

      closeSuggestions();
      return;
    }

    updateMentionContext(
      textarea.value,
      selectionStart,
    );
  };

  const handleScroll = () => {
    const textarea = textareaRef.current;
    const highlight = highlightRef.current;

    if (!textarea || !highlight) {
      return;
    }

    highlight.scrollTop = textarea.scrollTop;
    highlight.scrollLeft = textarea.scrollLeft;
  };

  const selectSuggestion = (user: MentionUser) => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    // Always use the actual textarea value rather than
    // relying on a potentially stale controlled prop.
    const currentValue = textarea.value;

    // Recalculate the mention context using the current
    // cursor position instead of relying on stale state.
    const currentContext = getMentionContext(
      currentValue,
      textarea.selectionStart,
    );

    if (!currentContext) {
      closeSuggestions();
      return;
    }

    const beforeMention = currentValue.slice(
      0,
      currentContext.start,
    );

    const afterMention = currentValue.slice(
      currentContext.end,
    );

    const insertedText = `@${user.username} `;

    const nextValue =
      beforeMention + insertedText + afterMention;

    // Position immediately after the inserted username
    // and its trailing space.
    const nextCaretPosition =
      beforeMention.length + insertedText.length;

    // Set this before notifying the parent.
    pendingCaretRef.current = {
      position: nextCaretPosition,
      value: nextValue,
    };

    suppressAutocompleteRef.current = false;

    closeSuggestions();

    setHasSelection(false);

    onChange(nextValue);
  };

  const handleKeyDown = (
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    const textarea = event.currentTarget;

    if (
      !isComposingRef.current &&
      !event.nativeEvent.isComposing
    ) {
      const selectionStart = textarea.selectionStart;
      const selectionEnd = textarea.selectionEnd;

      const hasCollapsedSelection =
        selectionStart === selectionEnd;

      const token = hasCollapsedSelection
        ? getMentionTokenAtPosition(
            textarea.value,
            selectionStart,
          )
        : null;

      /**
       * Arrow navigation skips over the mention token.
       *
       * Left: jump to before @.
       * Right: jump to after the username.
       */
      if (
        token &&
        event.key === 'ArrowLeft'
      ) {
        event.preventDefault();

        textarea.setSelectionRange(
          token.start,
          token.start,
        );

        setHasSelection(false);
        closeSuggestions();

        return;
      }

      if (
        token &&
        event.key === 'ArrowRight'
      ) {
        event.preventDefault();

        textarea.setSelectionRange(
          token.end,
          token.end,
        );

        setHasSelection(false);
        closeSuggestions();

        return;
      }

      /**
       * Allow Backspace and Delete to remove mention
       * characters individually.
       *
       * Suppress autocomplete while doing so, otherwise
       * each deletion would trigger another API request.
       */
      if (
        event.key === 'Backspace' ||
        event.key === 'Delete'
      ) {
        const tokenBeforeCaret =
          getMentionTokenAtPosition(
            textarea.value,
            selectionStart,
          );

        const tokenAfterCaret =
          selectionStart === selectionEnd
            ? getMentionTokenAtPosition(
                textarea.value,
                selectionStart + 1,
              )
            : null;

        if (
          token ||
          tokenBeforeCaret ||
          tokenAfterCaret
        ) {
          suppressAutocompleteRef.current = true;
          closeSuggestions();
        }
      } else {
        suppressAutocompleteRef.current = false;
      }

      if (suggestionsVisible) {
        if (
          event.key === 'ArrowDown' &&
          suggestions.length > 0
        ) {
          event.preventDefault();

          setActiveSuggestionIndex((current) =>
            current >= suggestions.length - 1
              ? 0
              : current + 1,
          );

          return;
        }

        if (
          event.key === 'ArrowUp' &&
          suggestions.length > 0
        ) {
          event.preventDefault();

          setActiveSuggestionIndex((current) =>
            current <= 0
              ? suggestions.length - 1
              : current - 1,
          );

          return;
        }

        if (
          event.key === 'Enter' &&
          suggestions.length > 0
        ) {
          event.preventDefault();

          selectSuggestion(
            suggestions[activeSuggestionIndex],
          );

          return;
        }

        if (event.key === 'Escape') {
          event.preventDefault();
          closeSuggestions();
          return;
        }
      }
    }

    onEditorKeyDown?.(event);
  };

  const handleCompositionStart = (
    event: CompositionEvent<HTMLTextAreaElement>,
  ) => {
    isComposingRef.current = true;

    onCompositionStart?.(event);
  };

  const handleCompositionEnd = (
    event: CompositionEvent<HTMLTextAreaElement>,
  ) => {
    isComposingRef.current = false;

    suppressAutocompleteRef.current = false;

    onCompositionEnd?.(event);

    updateMentionContext(
      event.currentTarget.value,
      event.currentTarget.selectionStart,
    );
  };

  const handleBlur = () => {
    closeSuggestions();
    onBlur?.();
  };

  const dropdownStyle: CSSProperties | undefined =
    dropdownPosition
      ? {
          position: 'fixed',
          left: dropdownPosition.left,
          top: dropdownPosition.top,
          width: dropdownPosition.width,
          maxHeight: dropdownPosition.maxHeight,
          transform:
            dropdownPosition.placement === 'above'
              ? 'translateY(-100%)'
              : undefined,
          zIndex: 9999,
        }
      : undefined;

  const mentionDropdown =
    suggestionsVisible &&
    dropdownPosition &&
    typeof document !== 'undefined'
      ? createPortal(
          <div
            style={dropdownStyle}
            className="overflow-y-auto rounded-xl border border-light-border bg-light-bg shadow-xl dark:border-dark-border dark:bg-dark-bg"
            role="listbox"
            aria-label="Mention suggestions"
          >
            <div className="border-b border-light-border px-3 py-2 dark:border-dark-border">
              <p className="text-xs font-semibold text-light-text-muted dark:text-dark-text-muted">
                {mentionContext?.query
                  ? 'People you may know'
                  : 'Recently mentioned'}
              </p>
            </div>

            {isLoading && (
              <div className="px-3 py-3 text-sm text-light-text-muted dark:text-dark-text-muted">
                Loading suggestions...
              </div>
            )}

            {!isLoading &&
              suggestions.length === 0 && (
                <div className="px-3 py-3 text-sm text-light-text-muted dark:text-dark-text-muted">
                  No matching users found.
                </div>
              )}

            {!isLoading &&
              suggestions.map((user, index) => (
                <button
                  key={user.id}
                  type="button"
                  role="option"
                  aria-selected={
                    index === activeSuggestionIndex
                  }
                  onPointerDown={(event) =>
                    event.preventDefault()
                  }
                  onClick={() =>
                    selectSuggestion(user)
                  }
                  className={[
                    'flex w-full items-center gap-3 px-3 py-2 text-left transition-colors',
                    index === activeSuggestionIndex
                      ? 'bg-light-surface-soft dark:bg-dark-surface-soft'
                      : 'hover:bg-light-surface-soft dark:hover:bg-dark-surface-soft',
                  ].join(' ')}
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-teal/10 text-sm font-semibold text-brand-teal">
                    {user.username
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex min-w-0 items-center gap-1.5">
                      <p className="truncate text-sm font-medium text-light-text dark:text-dark-text">
                        {user.display_name || user.username}
                      </p>

                      {user.is_verified && (
                        <VerificationBadge
                          type="verified"
                          size={16}
                        />
                      )}

                      {user.is_identity_verified && (
                        <VerificationBadge
                          type="identity"
                          size={16}
                        />
                      )}
                    </div>

                    <p className="truncate text-xs text-light-text-muted dark:text-dark-text-muted">
                      @{user.username}
                    </p>
                  </div>
                </button>
              ))}
          </div>,
          document.body,
        )
      : null;

  const textareaTextClass = hasSelection
    ? 'text-light-text selection:text-light-text dark:text-dark-text dark:selection:text-dark-text'
    : 'text-transparent selection:text-transparent';

  return (
    <div
      className={[
        'relative w-full',
        containerClassName,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {mentionDropdown}

      <div className="relative">
        {!hasSelection && (
          <div
            ref={highlightRef}
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 overflow-hidden whitespace-pre-wrap break-words rounded-xl border border-transparent px-4 py-3 text-sm leading-6 text-light-text dark:text-dark-text"
          >
            {value
              ? renderHighlightedText(value)
              : null}
          </div>
        )}

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onSelect={handleCursorChange}
          onClick={handleCursorChange}
          onKeyUp={handleCursorChange}
          onKeyDown={handleKeyDown}
          onCompositionStart={handleCompositionStart}
          onCompositionEnd={handleCompositionEnd}
          onScroll={handleScroll}
          onBlur={handleBlur}
          onFocus={onFocus}
          placeholder={placeholder}
          rows={autoResize ? 1 : rows}
          maxLength={maxLength}
          disabled={disabled}
          spellCheck
          className={[
            DEFAULT_TEXTAREA_CLASS,
            textareaTextClass,
            className,
          ]
            .filter(Boolean)
            .join(' ')}
          style={{
            WebkitTextFillColor: hasSelection
              ? 'currentColor'
              : 'transparent',
          }}
          aria-label={placeholder}
          aria-autocomplete="list"
          aria-controls={
            suggestionsVisible
              ? 'mention-suggestions'
              : undefined
          }
        />
      </div>
    </div>
  );
}
