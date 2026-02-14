import type { Editor } from '@tiptap/core';

class EditorState {
	editor = $state<Editor | null>(null);

	get isBold(): boolean {
		return this.editor?.isActive('bold') ?? false;
	}

	get isItalic(): boolean {
		return this.editor?.isActive('italic') ?? false;
	}

	get isStrike(): boolean {
		return this.editor?.isActive('strike') ?? false;
	}

	get isHeading1(): boolean {
		return this.editor?.isActive('heading', { level: 1 }) ?? false;
	}

	get isHeading2(): boolean {
		return this.editor?.isActive('heading', { level: 2 }) ?? false;
	}

	get isHeading3(): boolean {
		return this.editor?.isActive('heading', { level: 3 }) ?? false;
	}

	get isBulletList(): boolean {
		return this.editor?.isActive('bulletList') ?? false;
	}

	get isOrderedList(): boolean {
		return this.editor?.isActive('orderedList') ?? false;
	}

	get isBlockquote(): boolean {
		return this.editor?.isActive('blockquote') ?? false;
	}

	get isCodeBlock(): boolean {
		return this.editor?.isActive('codeBlock') ?? false;
	}

	get canUndo(): boolean {
		return this.editor?.can().undo() ?? false;
	}

	get canRedo(): boolean {
		return this.editor?.can().redo() ?? false;
	}
}

export const editorState = new EditorState();
